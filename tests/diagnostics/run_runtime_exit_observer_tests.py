# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Exercise the real Windows observer against disposable child processes, never Civ4.
# Check abnormal/ordinary exits, PID/start identity, superseding snapshots, torn history and concurrent observers using actual file locks and process handles. (GPT-6.1-Sol) -->
import ctypes
# <!-- custom: Construct a future status timestamp to verify that a later snapshot is labelled as such, rather than silently presented as earlier fault context. (GPT-6.1-Sol) -->
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
# <!-- custom: sys launches disposable Python children, tempfile isolates their files, and time bounds test-only waits for the attachment receipt/final output. (GPT-6.1-Sol) -->
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[2]
OBSERVER = ROOT / "Assets/SASRuntimeExitObserver.ps1"
# <!-- custom: Civ4's 32-bit DLL starts the WOW64 PowerShell on a 64-bit host; exercise that actual observer architecture by default, with System32 as the 32-bit-Windows fallback. (GPT-6.1-Sol) -->
WINDOWS_ROOT = Path(os.environ["SystemRoot"])
POWERSHELL = WINDOWS_ROOT / "SysWOW64/WindowsPowerShell/v1.0/powershell.exe"
if not POWERSHELL.is_file():
    POWERSHELL = WINDOWS_ROOT / "System32/WindowsPowerShell/v1.0/powershell.exe"


def process_start_utc(target):
    # <!-- custom: Match the production FILETIME millisecond identity without launching another shell or guessing creation time from the test clock. (GPT-6.1-Sol) -->
    from ctypes import wintypes
    from datetime import datetime, timedelta, timezone

    stamps = [wintypes.FILETIME() for _ in range(4)]
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
    if not kernel.GetProcessTimes(int(target._handle), *(ctypes.byref(stamp) for stamp in stamps)):
        raise ctypes.WinError(ctypes.get_last_error())
    ticks = (stamps[0].dwHighDateTime << 32) | stamps[0].dwLowDateTime
    value = datetime(1601, 1, 1, tzinfo=timezone.utc) + timedelta(milliseconds=ticks // 10000)
    return value.strftime("%Y%m%dT%H%M%S.") + "%03dZ" % (value.microsecond // 1000)


# <!-- custom: The optional fallback case runs a copied script without its C# companion, verifying that unavailable dialog monitoring does not suppress the original process-exit result. (GPT-6.1-Sol) -->
def run_case(folder, name, code=0, clean=False, mismatch=False, superseded=False, torn=False, blocked=False, copies=1, corrupt=False, missing=False, fallback=False):
    case = folder / name
    case.mkdir()
    trigger = case / "exit-now"
    program = "import ctypes,time,pathlib; p=pathlib.Path(%r)\nwhile not p.exists(): time.sleep(.02)\nctypes.windll.kernel32.ExitProcess(ctypes.c_uint32(%d))" % (str(trigger), code)
    target = subprocess.Popen([sys.executable, "-c", program])
    watchers = []
    try:
        started = process_start_utc(target)
        history_name = "SASRuntimeHistory_%s_%d.jsonl" % (started, target.pid)
        status = {
            "revision": 10, "processId": target.pid, "processStartUtc": started,
            "processState": "EXITED_CLEANLY" if clean else "RUNNING", "statusSerial": 12,
            "updatedUtc": started, "updateReason": "TURN_COMPLETED", "activity": "PLAYING", "sessionSerial": 2, "gameTurn": 290,
            "historyFilename": history_name, "historyAtCurrentRoot": 1,
            "historyRowsWritten": 0, "historyWriteFailures": 0,
        }
        path = case / "SASRuntimeStatus.json"
        path.write_text(json.dumps(status), encoding="utf-8")
        history = case / history_name
        if blocked:
            history.mkdir()
        elif torn:
            history.write_bytes(b'{"record":"interrupted')
        observer_script = OBSERVER
        if fallback:
            observer_script = case / "SASRuntimeExitObserver.ps1"
            observer_script.write_bytes(OBSERVER.read_bytes())
            # <!-- custom: Keep the shared metadata dependency present while deliberately omitting only the C# listener in this fallback case. (GPT-6.1-Sol) -->
            (case / "SASRuntimeObserverEnvironment.ps1").write_bytes((ROOT / "Assets/SASRuntimeObserverEnvironment.ps1").read_bytes())
        for _ in range(copies):
            watchers.append(subprocess.Popen([
                str(POWERSHELL), "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                "-File", str(observer_script), "-StatusPath", str(path), "-TargetProcessId", str(target.pid),
                "-ProcessStartUtc", "wrong-start" if mismatch else started, "-RecorderRevision", "10",
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW))
        # <!-- custom: Wait for the actual attachment receipt before releasing the target; these tests concern observed exits, not the documented pre-attachment coverage gap. (GPT-6.1-Sol) -->
        evidence_path = case / ("SASRuntimeExit_%s_%d.json" % (started, target.pid))
        if mismatch:
            # <!-- custom: A fixed 0.5-second sleep did not guarantee the identity check finished; the fixture could release the target first and get attachment failure (3) instead of wrong-start rejection (2).
            # Wait for rejection while the target is alive so this case tests identity matching rather than observer startup speed. (GPT-6.1-Sol) -->
            for watcher in watchers:
                watcher.wait(timeout=10)
            assert target.poll() is None
        else:
            deadline = time.monotonic() + 10
            receipt = {}
            while time.monotonic() < deadline:
                if evidence_path.exists():
                    receipt = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
                    if receipt.get("dialogObserverState") in ("ACTIVE", "UNAVAILABLE"):
                        break
                time.sleep(.05)
            assert receipt.get("dialogObserverState") == ("UNAVAILABLE" if fallback else "ACTIVE"), receipt
            assert receipt["environment"]["powershellVersion"] and receipt["environment"]["processBits"] in (32, 64), receipt
            assert receipt["listenerCompilation"]["state"] == ("FAILED" if fallback else "SUCCEEDED"), receipt
            assert receipt["listenerCompilation"]["elapsedMilliseconds"] >= 0, receipt
            if name == "ordinary":
                print("Observed listenerCompilation:", json.dumps(receipt["listenerCompilation"]))
            assert receipt["observerState"] == "WAITING" and receipt["processId"] == target.pid, receipt
        if superseded:
            status["processId"] += 1
            path.write_text(json.dumps(status), encoding="utf-8")
        if corrupt:
            path.write_bytes(b'{"torn')
        if missing:
            path.unlink()
        before = path.read_bytes() if path.exists() else None
        trigger.touch()
        target.wait(timeout=10)
        for watcher in watchers:
            stdout, stderr = watcher.communicate(timeout=15)
            expected = 2 if mismatch else (4 if corrupt else 0)
            assert watcher.returncode == expected, (name, watcher.returncode, stdout, stderr)
        if not mismatch:
            evidence = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
            assert evidence["observerState"] == "EXITED" and evidence["exitCodeHex"] == "0x%08X" % code, evidence
            assert evidence["dialogObserverState"] == ("UNAVAILABLE" if fallback else "ACTIVE"), evidence
            # <!-- custom: Screenshot collection is independently default-off even with exit/dialog observation active; no screenshot child/state/history may appear. (GPT-6.1-Sol) -->
            assert evidence["screenshotObserverState"] == "DISABLED" and evidence["screenshotObserverProcessId"] == 0, evidence
            assert not list(case.glob("SASRuntimeScreenshot*.json*")), name
        if corrupt or missing:
            assert (path.read_bytes() if path.exists() else None) == before, name
            print("PASS", name)
            return
        result = json.loads(path.read_text(encoding="utf-8-sig"))
        if mismatch or superseded:
            assert path.read_bytes() == before, name
        else:
            observed = result["exitObservation"]
            assert observed["exitCodeHex"] == "0x%08X" % code, result
            assert observed["outcome"] == ("ZERO_EXIT_CODE" if code == 0 else "NONZERO_EXIT_CODE"), result
            assert result["processState"] == ("EXITED_CLEANLY" if clean and code == 0 else "EXITED"), result
            assert result["gameTurn"] == 290 and result["activity"] == "PLAYING", result
            assert result["statusSerial"] == 13, result
            if blocked:
                assert observed["historyAppend"] == "WRITE_FAILED" and result["historyWriteFailures"] == 1, result
            else:
                rows = history.read_text(encoding="utf-8").splitlines()
                exits = [json.loads(row) for row in rows if '"record":"process_exit"' in row]
                assert len(exits) == 1 and exits[0]["exitCodeHex"] == observed["exitCodeHex"], rows
                assert result["historyRowsWritten"] == 1, result
                if torn:
                    assert observed["unterminatedHistoryTail"], observed
                    assert rows[0] == '{"record":"interrupted', rows
        print("PASS", name)
    finally:
        if target.poll() is None:
            target.terminate()
            target.wait(timeout=10)
        for watcher in watchers:
            if watcher.poll() is None:
                watcher.terminate()
                watcher.wait(timeout=10)


# <!-- custom: Add optional context_variant so the real failure reader sees future, oversized or mismatched snapshots after successful attachment; the default retains ordinary dialog tests. (GPT-6.1-Sol) -->
def run_dialog_case(folder, executable, mode, context_variant="normal"):
    case = folder / ("dialog-" + mode + ("-" + context_variant if context_variant != "normal" else ""))
    case.mkdir()
    target = subprocess.Popen([str(executable), str(case), "ordinary" if mode == "foreign" else mode])
    foreign = None
    if mode == "foreign":
        foreign_root = case / "foreign"
        foreign_root.mkdir()
        foreign = subprocess.Popen([str(executable), str(foreign_root), "existing"])
    watcher = None
    try:
        started = process_start_utc(target)
        path = case / "SASRuntimeStatus.json"
        history_name = "SASRuntimeHistory_%s_%d.jsonl" % (started, target.pid)
        path.write_text(json.dumps({
            "revision": 16, "processId": target.pid, "processStartUtc": started,
            "processState": "RUNNING", "statusSerial": 41, "updateReason": "PLAYER_TURN_PROGRESS",
            "updatedUtc": started, "sessionSerial": 3, "sessionKind": "LOAD_GAME", "activity": "PLAYING",
            "gameTurn": 123, "elapsedGameTurns": 124, "activePlayer": 4, "autoplayActive": 0,
            "playerTurnPlayer": 8, "playerTurnTeam": 6, "playerTurnCivilization": 12,
            "playerTurnCivilizationType": "CIVILIZATION_TEST", "playerTurnControl": "AI",
            "playerTurnPhase": "AI_MOVES", "playerTurnElapsedMilliseconds": 4567,
            "worldBuilderMode": 0, "worldBuilderScreenVisible": 0,
            "civilopediaVisible": 1, "civilopediaContext": "UNIT",
            "buttonPopupAwaitingInteraction": 0, "buttonPopupType": "NONE",
            "historyFilename": history_name, "historyAtCurrentRoot": 1,
            "historyRowsWritten": 0, "historyWriteFailures": 0,
        }), encoding="utf-8")
        watcher = subprocess.Popen([str(POWERSHELL), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(OBSERVER), "-StatusPath", str(path), "-TargetProcessId", str(target.pid), "-ProcessStartUtc", started, "-RecorderRevision", "16"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
        evidence_path = case / ("SASRuntimeExit_%s_%d.json" % (started, target.pid))

        def await_evidence(predicate):
            evidence = {}
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                if evidence_path.exists():
                    # <!-- custom: The live observer atomically replaces its receipt; Windows sharing can briefly reject this fixture's read.
                    # Retry within the existing deadline rather than mistake that transient read race for an observer failure. (GPT-6.1-Sol) -->
                    try:
                        evidence = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
                    except (OSError, ValueError):
                        time.sleep(.05)
                        continue
                    if predicate(evidence):
                        return evidence
                time.sleep(.03)
            raise AssertionError((mode, evidence))

        await_evidence(lambda value: value.get("dialogObserverState") == "ACTIVE")
        # <!-- custom: Change only the disposable status file after attachment; this tests the failure-context reader independently of the observer's initial PID/start launch guard. (GPT-6.1-Sol) -->
        if context_variant != "normal":
            status = json.loads(path.read_text(encoding="utf-8"))
            if context_variant == "future":
                status["updatedUtc"] = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y%m%dT%H%M%S.000Z")
            elif context_variant == "oversized":
                status["oversizedFixture"] = "x" * 65537
            elif context_variant == "identity":
                status["processStartUtc"] = "mismatched fixture start"
            else:
                raise AssertionError(context_variant)
            path.write_text(json.dumps(status), encoding="utf-8")
        (case / "show-now").touch()
        unrecognized = mode in ("ordinary", "assertion", "foreign", "dump-invalid", "video-invalid")
        if unrecognized:
            time.sleep(.4)
            evidence = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
            assert evidence["failureDialogCount"] == 0, evidence
        else:
            expected_kind = ("CIV4_CRASH_DUMP_PROMPT" if mode.startswith("dump-") else
                "CIV4_VIDEO_MEMORY_ALLOCATION_FAILURE" if mode.startswith("video-") else "MSVC_RUNTIME_ERROR")
            evidence = await_evidence(lambda value: value.get("failureDialogCount") == 1)
            assert evidence["observerState"] == "WAITING" and target.poll() is None, evidence
            failure = evidence["failureDialog"]
            assert failure["visible"] and failure["kind"] == expected_kind, evidence
            expected_text = "diagnostic file?" if mode.startswith("dump-") else "Failed to allocate video memory." if mode.startswith("video-") else "caf\u00e9"
            assert expected_text in failure["text"], evidence
            assert json.loads(path.read_text())["processState"] == "RUNNING"
            # <!-- custom: Runtime16 samples memory/status once when a reviewed failure becomes visible.
            # Values are context, not a diagnosis; explicitly unmeasured target free-VA/GPU-VRAM must stay labelled as such. (ChatGPT-5.6-Sol) -->
            memory = failure["memory"]
            assert memory["processMemoryState"] == "AVAILABLE", memory
            assert memory["processWorkingSetBytes"] > 0 and memory["processPrivateBytes"] > 0 and memory["processVirtualBytes"] > 0, memory
            assert memory["systemMemoryState"] in ("AVAILABLE", "PARTIAL"), memory
            if memory["systemMemoryState"] == "AVAILABLE":
                assert memory["systemPhysicalAvailableBytes"] >= 0 and memory["systemCommitLimitBytes"] > 0, memory
                assert 0 <= memory["systemCommitTotalBytes"] <= memory["systemCommitLimitBytes"], memory
                assert memory["systemCommitAvailableBytes"] == memory["systemCommitLimitBytes"] - memory["systemCommitTotalBytes"], memory
            assert memory["processImageState"] in ("AVAILABLE", "PARTIAL", "FAILED"), memory
            if memory["processImageState"] in ("AVAILABLE", "PARTIAL"):
                assert memory["processImagePe32"] in (-1, 0, 1) and memory["processImageLargeAddressAware"] in (0, 1), memory
                assert memory["processImageMachine"].startswith("0x"), memory
            assert memory["operatingSystemBits"] in (32, 64), memory
            assert memory["targetFreeVirtualBytesState"] == "NOT_MEASURED" and memory["gpuVideoMemoryState"] == "NOT_MEASURED", memory
            context = failure["runtimeContext"]
            expected_context_state = {"oversized": "STATUS_TOO_LARGE", "identity": "STATUS_IDENTITY_MISMATCH"}.get(context_variant, "MATCHED_PROCESS_STATUS_CONTEXT_MAY_BE_STALE")
            assert context["state"] == expected_context_state, context
            if context_variant in ("normal", "future"):
                assert context["statusAgeMilliseconds"] >= 0, context
                assert context["statusTimestampRelation"] == ("AFTER_DIALOG_OBSERVATION" if context_variant == "future" else "AT_OR_BEFORE_DIALOG_OBSERVATION"), context
                assert context["statusSerial"] == 41 and context["sessionSerial"] == 3 and context["sessionKind"] == "LOAD_GAME", context
                assert context["gameTurn"] == 123 and context["activePlayer"] == 4 and context["playerTurnPlayer"] == 8, context
                assert context["playerTurnCivilizationType"] == "CIVILIZATION_TEST" and context["playerTurnPhase"] == "AI_MOVES", context
            else:
                assert context["gameTurn"] == -1 and context["statusTimestampRelation"] == "UNKNOWN", context
            if mode in ("after", "dump-after", "video-after"):
                before_memory = dict(memory)
                before_context = dict(context)
                (case / "close-now").touch()
                evidence = await_evidence(lambda value: value.get("failureDialog") and not value["failureDialog"]["visible"])
                assert evidence["failureDialogCount"] == 1 and target.poll() is None, evidence
                assert evidence["failureDialog"]["memory"] == before_memory, evidence
                assert evidence["failureDialog"]["runtimeContext"] == before_context, evidence
        status_before_exit = path.read_bytes()
        (case / "exit-now").touch()
        target.wait(timeout=10)
        stdout, stderr = watcher.communicate(timeout=10)
        assert watcher.returncode == 0, (stdout, stderr)
        # <!-- custom: A mismatched current snapshot belongs to another identity and must remain untouched; the independent exit receipt still retains this target's failure and final exit. (GPT-6.1-Sol) -->
        if context_variant == "identity":
            receipt = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
            assert receipt["observerState"] == "EXITED" and receipt["exitCode"] == 7, receipt
            assert receipt["failureDialog"]["runtimeContext"]["state"] == "STATUS_IDENTITY_MISMATCH", receipt
            assert path.read_bytes() == status_before_exit and not (case / history_name).exists(), receipt
            print("PASS dialog", mode, context_variant)
            return
        final = json.loads(path.read_text(encoding="utf-8-sig"))
        assert final["processState"] == "EXITED" and final["exitObservation"]["exitCode"] == 7, final
        rows = [json.loads(row) for row in (case / history_name).read_text().splitlines()]
        assert len(rows) == 1 and rows[0]["record"] == "process_exit", rows
        recognized = mode in ("existing", "after", "dump-existing", "dump-after", "video-existing", "video-after", "video-old-existing")
        if recognized:
            assert rows[0]["failureDialogCount"] == 1 and rows[0]["failureDialog"]["kind"] == expected_kind, rows
            assert rows[0]["failureDialog"]["runtimeContext"]["state"] == expected_context_state, rows
            assert rows[0]["failureDialog"]["memory"]["targetFreeVirtualBytesState"] == "NOT_MEASURED", rows
            assert final["exitObservation"]["failureDialogKind"] == expected_kind, final
        else:
            assert "failureDialog" not in rows[0], rows
        print("PASS dialog", mode, context_variant)
    finally:
        if target.poll() is None:
            target.terminate()
            target.wait(timeout=10)
        if foreign is not None and foreign.poll() is None:
            foreign.terminate()
            foreign.wait(timeout=10)
        if watcher is not None and watcher.poll() is None:
            watcher.terminate()
            watcher.wait(timeout=10)


def main():
    with tempfile.TemporaryDirectory(prefix="SAS exit \u00e9 ' ") as temporary:
        folder = Path(temporary)
        run_case(folder, "ordinary")
        run_case(folder, "native-clean", clean=True)
        run_case(folder, "simulated-access-violation-code", code=0xC0000005, clean=True)
        run_case(folder, "wrong-start", mismatch=True)
        run_case(folder, "newer-game-snapshot", superseded=True)
        run_case(folder, "torn-history", code=7, torn=True)
        run_case(folder, "history-unwritable", code=7, blocked=True)
        run_case(folder, "two-observers", code=7, copies=2)
        run_case(folder, "torn-status", code=7, corrupt=True)
        run_case(folder, "retired-status", code=7, missing=True)
        run_case(folder, "missing-dialog-companion", code=7, fallback=True)
        executable = folder / "dialog-fixture.exe"
        source = ROOT / "tests/diagnostics/runtime_dialog_fixture.cs"
        command = "Add-Type -Path '%s' -OutputAssembly '%s' -OutputType WindowsApplication" % (str(source).replace("'", "''"), str(executable).replace("'", "''"))
        subprocess.run([str(POWERSHELL), "-NoProfile", "-NonInteractive", "-Command", command], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        for mode in ("existing", "after", "ordinary", "assertion", "foreign", "dump-existing", "dump-after", "dump-invalid",
                "video-existing", "video-after", "video-old-existing", "video-invalid"):
            run_dialog_case(folder, executable, mode)
        for context_variant in ("future", "oversized", "identity"):
            run_dialog_case(folder, executable, "video-after", context_variant)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

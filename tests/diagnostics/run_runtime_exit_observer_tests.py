# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Exercise the real Windows observer against disposable child processes, never Civ4.
# Check abnormal/ordinary exits, PID/start identity, superseding snapshots, torn history and concurrent observers using actual file locks and process handles. (GPT-6.1-Sol) -->
import ctypes
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
        for _ in range(copies):
            watchers.append(subprocess.Popen([
                str(POWERSHELL), "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                "-File", str(observer_script), "-StatusPath", str(path), "-TargetProcessId", str(target.pid),
                "-ProcessStartUtc", "wrong-start" if mismatch else started, "-RecorderRevision", "10",
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW))
        # <!-- custom: Wait for the actual attachment receipt before releasing the target; these tests concern observed exits, not the documented pre-attachment coverage gap. (GPT-6.1-Sol) -->
        evidence_path = case / ("SASRuntimeExit_%s_%d.json" % (started, target.pid))
        if mismatch:
            time.sleep(.5)
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


def run_dialog_case(folder, executable, mode):
    case = folder / ("dialog-" + mode)
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
            "revision": 11, "processId": target.pid, "processStartUtc": started,
            "processState": "RUNNING", "statusSerial": 1, "updateReason": "TURN_COMPLETED",
            "updatedUtc": started, "activity": "PLAYING", "sessionSerial": 1, "gameTurn": 5,
            "historyFilename": history_name, "historyAtCurrentRoot": 1,
            "historyRowsWritten": 0, "historyWriteFailures": 0,
        }), encoding="utf-8")
        watcher = subprocess.Popen([str(POWERSHELL), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(OBSERVER), "-StatusPath", str(path), "-TargetProcessId", str(target.pid), "-ProcessStartUtc", started, "-RecorderRevision", "11"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
        evidence_path = case / ("SASRuntimeExit_%s_%d.json" % (started, target.pid))

        def await_evidence(predicate):
            evidence = {}
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                if evidence_path.exists():
                    evidence = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
                    if predicate(evidence):
                        return evidence
                time.sleep(.03)
            raise AssertionError((mode, evidence))

        await_evidence(lambda value: value.get("dialogObserverState") == "ACTIVE")
        (case / "show-now").touch()
        if mode in ("ordinary", "assertion", "foreign", "dump-invalid"):
            time.sleep(.4)
            evidence = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
            assert evidence["failureDialogCount"] == 0, evidence
        else:
            expected_kind = "CIV4_CRASH_DUMP_PROMPT" if mode.startswith("dump-") else "MSVC_RUNTIME_ERROR"
            evidence = await_evidence(lambda value: value.get("failureDialogCount") == 1)
            assert evidence["observerState"] == "WAITING" and target.poll() is None, evidence
            assert evidence["failureDialog"]["visible"] and evidence["failureDialog"]["kind"] == expected_kind, evidence
            assert ("diagnostic file?" if mode.startswith("dump-") else "caf\u00e9") in evidence["failureDialog"]["text"], evidence
            assert json.loads(path.read_text())["processState"] == "RUNNING"
            if mode in ("after", "dump-after"):
                (case / "close-now").touch()
                evidence = await_evidence(lambda value: value.get("failureDialog") and not value["failureDialog"]["visible"])
                assert evidence["failureDialogCount"] == 1 and target.poll() is None, evidence
        (case / "exit-now").touch()
        target.wait(timeout=10)
        stdout, stderr = watcher.communicate(timeout=10)
        assert watcher.returncode == 0, (stdout, stderr)
        final = json.loads(path.read_text(encoding="utf-8-sig"))
        assert final["processState"] == "EXITED" and final["exitObservation"]["exitCode"] == 7, final
        rows = [json.loads(row) for row in (case / history_name).read_text().splitlines()]
        assert len(rows) == 1 and rows[0]["record"] == "process_exit", rows
        if mode in ("existing", "after", "dump-existing", "dump-after"):
            assert rows[0]["failureDialogCount"] == 1 and rows[0]["failureDialog"]["kind"] == expected_kind, rows
            assert final["exitObservation"]["failureDialogKind"] == expected_kind, final
        else:
            assert "failureDialog" not in rows[0], rows
        print("PASS dialog", mode)
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
        for mode in ("existing", "after", "ordinary", "assertion", "foreign", "dump-existing", "dump-after", "dump-invalid"):
            run_dialog_case(folder, executable, mode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

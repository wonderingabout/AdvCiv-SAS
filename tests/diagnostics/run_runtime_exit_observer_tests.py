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
POWERSHELL = Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"


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


def run_case(folder, name, code=0, clean=False, mismatch=False, superseded=False, torn=False, blocked=False, copies=1, corrupt=False, missing=False):
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
        for _ in range(copies):
            watchers.append(subprocess.Popen([
                str(POWERSHELL), "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                "-File", str(OBSERVER), "-StatusPath", str(path), "-TargetProcessId", str(target.pid),
                "-ProcessStartUtc", "wrong-start" if mismatch else started, "-RecorderRevision", "10",
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW))
        # <!-- custom: Wait for the actual attachment receipt before releasing the target; these tests concern observed exits, not the documented pre-attachment coverage gap. (GPT-6.1-Sol) -->
        evidence_path = case / ("SASRuntimeExit_%s_%d.json" % (started, target.pid))
        if mismatch:
            time.sleep(.5)
        else:
            deadline = time.monotonic() + 10
            while not evidence_path.exists() and time.monotonic() < deadline:
                time.sleep(.05)
            assert evidence_path.exists(), name
            receipt = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
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


def main():
    with tempfile.TemporaryDirectory(prefix="SAS exit ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â© ' ") as temporary:
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

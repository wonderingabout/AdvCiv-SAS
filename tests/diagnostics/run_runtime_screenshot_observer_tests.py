# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Exercise the shipped Runtime 14 screenshot FileSystemWatcher against a disposable image directory/process rather than the user's real Civ4 ScreenShots folder.
# The fixture verifies future-file-only capture, burst coalescing, hashes, native-pattern classification, runtime-context correlation uncertainty, duplicate ownership and clean target exit. (ChatGPT-5.6-Sol) -->
# <!-- custom: ctypes reads the disposable target's exact Windows process-creation FILETIME so the production observer cannot attach to a reused PID. (ChatGPT-5.6-Sol) -->
import ctypes
# <!-- custom: struct/zlib construct a tiny valid PNG fixture so the production image reader is exercised without adding image libraries or copying real screenshots. (GPT-6.1-Sol) -->
import struct
import zlib
import hashlib
import json
import os
from pathlib import Path
# <!-- custom: subprocess launches only disposable target/PowerShell fixtures; no real Civ4 process or screenshot directory is touched. (ChatGPT-5.6-Sol) -->
import subprocess
# <!-- custom: sys supplies the disposable child interpreter used as the observer's target process. (ChatGPT-5.6-Sol) -->
import sys
# <!-- custom: tempfile isolates synthetic screenshot/log files from the user's real My Games tree. (ChatGPT-5.6-Sol) -->
import tempfile
# <!-- custom: time supplies bounded waits for asynchronous FileSystemWatcher/process events in this local Windows test. (ChatGPT-5.6-Sol) -->
import time

ROOT = Path(__file__).resolve().parents[2]
OBSERVER = ROOT / "Assets/SASRuntimeScreenshotObserver.ps1"
WINDOWS_ROOT = Path(os.environ.get("SystemRoot", "C:/Windows"))
POWERSHELL = WINDOWS_ROOT / "SysWOW64/WindowsPowerShell/v1.0/powershell.exe"
if not POWERSHELL.is_file():
    POWERSHELL = WINDOWS_ROOT / "System32/WindowsPowerShell/v1.0/powershell.exe"


def process_start_utc(target):
    # <!-- custom: Keep Windows-only FILETIME/UTC helpers local so the module can import and skip cleanly on non-Windows CI hosts. (ChatGPT-5.6-Sol) -->
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


def await_json(path, predicate, timeout=12):
    deadline = time.monotonic() + timeout
    value = {}
    while time.monotonic() < deadline:
        if path.is_file():
            value = json.loads(path.read_text(encoding="utf-8-sig"))
            if predicate(value):
                return value
        time.sleep(.05)
    raise AssertionError((path, value))


def await_rows(path, count, timeout=12):
    deadline = time.monotonic() + timeout
    rows = []
    while time.monotonic() < deadline:
        if path.is_file():
            rows = [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
            if len(rows) >= count:
                return rows
        time.sleep(.05)
    raise AssertionError((path, rows))


def main():
    if os.name != "nt":
        print("SKIP Runtime screenshot observer requires Windows")
        return 0
    with tempfile.TemporaryDirectory(prefix="SAS screenshot watch é ") as temporary:
        root = Path(temporary)
        logs = root / "Logs"
        screenshots = root / "ScreenShots"
        logs.mkdir()
        screenshots.mkdir()
        # <!-- custom: Existing screenshots must never be backfilled when a diagnostic observer attaches mid-run. (ChatGPT-5.6-Sol) -->
        (screenshots / "Civ4ScreenShot0001.JPG").write_bytes(b"pre-existing")

        trigger = root / "exit-now"
        program = "import pathlib,time; p=pathlib.Path(%r)\nwhile not p.exists(): time.sleep(.02)" % str(trigger)
        target = subprocess.Popen([sys.executable, "-c", program])
        watcher = None
        duplicate = None
        try:
            started = process_start_utc(target)
            status = logs / "SASRuntimeStatus.json"
            status.write_text(json.dumps({
                "revision": 14,
                "processId": target.pid,
                "processStartUtc": started,
                "updatedUtc": started,
                "statusSerial": 77,
                "sessionSerial": 3,
                "sessionKind": "LOAD_GAME",
                "gameState": "PLAYING",
                "activity": "PLAYING",
                "gameTurn": 123,
                "elapsedGameTurns": 124,
                "activePlayer": 4,
                "autoplayActive": 0,
                "playerTurnPlayer": 8,
                "playerTurnTeam": 6,
                "playerTurnCivilization": 12,
                "playerTurnCivilizationType": "CIVILIZATION_TEST",
                "playerTurnControl": "AI",
                "playerTurnPhase": "AI_MOVES",
                "playerTurnElapsedMilliseconds": 4567,
                "worldBuilderMode": 0,
                "worldBuilderScreenVisible": 0,
                "civilopediaVisible": 1,
                "civilopediaContext": "UNIT",
                "buttonPopupAwaitingInteraction": 0,
                "buttonPopupType": "NONE",
                "buttonPopupActivePlayer": -1,
            }), encoding="utf-8")
            command = [
                str(POWERSHELL), "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                "-File", str(OBSERVER), "-StatusPath", str(status), "-TargetProcessId", str(target.pid),
                "-ProcessStartUtc", started, "-RecorderRevision", "14", "-ScreenshotDirectory", str(screenshots),
            ]
            watcher = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
            state_path = logs / ("SASRuntimeScreenshotWatch_%s_%d.json" % (started, target.pid))
            rows_path = logs / ("SASRuntimeScreenshots_%s_%d.jsonl" % (started, target.pid))
            state = await_json(state_path, lambda value: value.get("observerState") == "WATCHING")
            assert state["filesRecorded"] == 0 and rows_path.read_text(encoding="utf-8-sig") == "", state
            assert state["environment"]["powershellVersion"] and state["environment"]["clrVersion"], state

            duplicate = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
            duplicate.communicate(timeout=10)
            assert duplicate.returncode == 0

            native_bytes = b"fake-jpeg-v1"
            native = screenshots / "Civ4ScreenShot4273.JPG"
            native.write_bytes(b"fake-jpeg-v0")
            time.sleep(.05)
            native.write_bytes(native_bytes)
            (screenshots / "ignored.txt").write_text("not a screenshot\n", encoding="utf-8")
            rows = await_rows(rows_path, 1)
            first = rows[0]
            assert first["filename"] == native.name and first["nativeCiv4FilenamePattern"] == 1, first
            assert first["writerIdentity"] == "NOT_OBSERVED" and first["captureRequestObserved"] == 0, first
            assert first["fingerprint"] == hashlib.sha256(native_bytes).hexdigest().upper(), first
            assert first["dimensionsStatus"] == "UNREADABLE_IMAGE" and first["imageWidth"] == -1, first
            assert first["associationState"] == "MATCHED_PROCESS_STATUS_CONTEXT_MAY_BE_STALE", first
            assert first["gameTurn"] == 123 and first["activePlayer"] == 4 and first["playerTurnPlayer"] == 8, first
            assert first["playerTurnTeam"] == 6 and first["playerTurnCivilizationType"] == "CIVILIZATION_TEST", first
            assert first["civilopediaContext"] == "UNIT" and first["runtimeStatusAgeMilliseconds"] >= 0, first

            def png_chunk(kind, data):
                return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)
            external_bytes = (
                b"\x89PNG\r\n\x1a\n"
                + png_chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 3, 8, 6, 0, 0, 0))
                + png_chunk(b"IDAT", zlib.compress((b"\0" + b"\xff\0\0\xff" * 2) * 3))
                + png_chunk(b"IEND", b"")
            )
            external = screenshots / "manual_capture.png"
            external.write_bytes(external_bytes)
            rows = await_rows(rows_path, 2)
            second = rows[1]
            assert second["filename"] == external.name and second["nativeCiv4FilenamePattern"] == 0, second
            assert second["writerIdentity"] == "NOT_OBSERVED", second
            assert (second["imageWidth"], second["imageHeight"], second["dimensionsStatus"]) == (2, 3, "AVAILABLE"), second
            assert second["fingerprint"] == hashlib.sha256(external_bytes).hexdigest().upper(), second
            assert all(row["filename"] != "Civ4ScreenShot0001.JPG" for row in rows), rows
            assert all(row["filename"] != "ignored.txt" for row in rows), rows

            trigger.touch()
            target.wait(timeout=10)
            stdout, stderr = watcher.communicate(timeout=15)
            assert watcher.returncode == 0, (stdout, stderr)
            final = await_json(state_path, lambda value: value.get("observerState") == "EXITED")
            assert final["filesRecorded"] == 2, final
            assert final["writeFailures"] == 0 and final["rowsDropped"] == 0 and final["watcherErrors"] == 0, final
            assert final["lastScreenshotFilename"] == external.name, final
            print("PASS Runtime screenshot observer: future files, coalescing, hashes, context, duplicate ownership and exit")
        finally:
            if target.poll() is None:
                target.terminate()
                target.wait(timeout=10)
            for process in (watcher, duplicate):
                if process is not None and process.poll() is None:
                    process.terminate()
                    process.wait(timeout=10)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

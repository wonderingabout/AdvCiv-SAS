# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Exercise the shipped Runtime 12 FileSystemWatcher companion against disposable Python/XML trees and a disposable process.
# The fixture verifies burst coalescing, final hashes, ignored files, deletion/rename evidence and clean observer shutdown without Civ4 or administrator rights. (ChatGPT-5.6-Sol) -->
# <!-- custom: Standard-library process/filesystem/JSON/time imports keep the watcher test self-contained and disposable; ctypes is used only to match the target process creation UTC exactly as the production observer requires. (ChatGPT-5.6-Sol) -->
import ctypes
# <!-- custom: Compare the observed fingerprint with known fixture bytes rather than accepting any 64-character string. (GPT-6.1-Sol) -->
import hashlib
import json
import os
from pathlib import Path
import subprocess
# <!-- custom: sys supplies the disposable child interpreter used as the watched target process. (ChatGPT-5.6-Sol) -->
import sys
# <!-- custom: tempfile isolates watcher output and edited fixture trees from the real mod installation. (ChatGPT-5.6-Sol) -->
import tempfile
# <!-- custom: time supplies bounded polling waits for asynchronous filesystem/process events in the test only. (ChatGPT-5.6-Sol) -->
import time

ROOT = Path(__file__).resolve().parents[2]
OBSERVER = ROOT / "Assets/SASRuntimeSourceObserver.ps1"
WINDOWS_ROOT = Path(os.environ["SystemRoot"])
POWERSHELL = WINDOWS_ROOT / "SysWOW64/WindowsPowerShell/v1.0/powershell.exe"
if not POWERSHELL.is_file():
    POWERSHELL = WINDOWS_ROOT / "System32/WindowsPowerShell/v1.0/powershell.exe"


def process_start_utc(target):
    # <!-- custom: Import Windows FILETIME and UTC conversion helpers locally because this path is Windows-only and the test must still import/skip cleanly on other CI hosts. (ChatGPT-5.6-Sol) -->
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


# <!-- custom: Force target exit immediately before the real exit-event subscription, using a test-only PowerShell command wrapper; the production script must finish rather than wait forever for an already-lost event. (GPT-6.1-Sol) -->
def run_exit_subscription_case(root):
    assets = root / "Assets"
    (assets / "Python").mkdir(parents=True)
    (assets / "XML").mkdir()
    logs = root / "Logs"
    logs.mkdir()
    target = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    watcher = None
    try:
        started = process_start_utc(target)
        wrapper = root / "subscription-race.ps1"
        wrapper.write_text(
            "function Register-ObjectEvent {\n"
            " param($InputObject, $EventName, $SourceIdentifier)\n"
            " if ($EventName -eq 'Exited') { $InputObject.Kill(); $InputObject.WaitForExit() }\n"
            " Microsoft.PowerShell.Utility\\Register-ObjectEvent -InputObject $InputObject -EventName $EventName -SourceIdentifier $SourceIdentifier\n"
            "}\n& '" + str(OBSERVER).replace("'", "''") + "' @args\n",
            encoding="utf-8-sig",
        )
        watcher = subprocess.Popen([
            str(POWERSHELL), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(wrapper),
            "-StatusPath", str(logs / "SASRuntimeStatus.json"), "-TargetProcessId", str(target.pid),
            "-ProcessStartUtc", started, "-RecorderRevision", "12", "-WatchRoot", str(assets),
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
        stdout, stderr = watcher.communicate(timeout=8)
        assert watcher.returncode == 0, (stdout, stderr)
        final = json.loads((logs / ("SASRuntimeSourceWatch_%s_%d.json" % (started, target.pid))).read_text(encoding="utf-8-sig"))
        assert final["observerState"] == "EXITED", final
        print("PASS Runtime source observer: target exit during subscription does not strand watcher")
    finally:
        for process in (target, watcher):
            if process is not None and process.poll() is None:
                process.terminate()
                process.wait(timeout=10)


def main():
    if os.name != "nt":
        print("SKIP Runtime source observer requires Windows")
        return 0
    with tempfile.TemporaryDirectory(prefix="SAS source watch é ") as temporary:
        root = Path(temporary)
        assets = root / "Assets"
        python = assets / "Python"
        xml = assets / "XML"
        logs = root / "Logs"
        python.mkdir(parents=True)
        xml.mkdir()
        (assets / "Config").mkdir()
        logs.mkdir()
        # <!-- custom: Broader runtime inputs use the same event journal; these fixture roots exist before subscription, just like shipped mod directories. (GPT-6.1-Sol) -->
        for directory in ("PrivateMaps", "Resource", "Settings"):
            (root / directory).mkdir()

        trigger = root / "exit-now"
        program = "import pathlib,time; p=pathlib.Path(%r)\nwhile not p.exists(): time.sleep(.02)" % str(trigger)
        target = subprocess.Popen([sys.executable, "-c", program])
        watcher = None
        duplicate = None
        try:
            started = process_start_utc(target)
            status = logs / "SASRuntimeStatus.json"
            status.write_text(json.dumps({"revision": 12, "processId": target.pid, "processStartUtc": started}), encoding="utf-8")
            command = [
                str(POWERSHELL), "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                "-File", str(OBSERVER), "-StatusPath", str(status), "-TargetProcessId", str(target.pid),
                "-ProcessStartUtc", started, "-RecorderRevision", "12", "-WatchRoot", str(assets),
            ]
            watcher = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
            state_path = logs / ("SASRuntimeSourceWatch_%s_%d.json" % (started, target.pid))
            rows_path = logs / ("SASRuntimeSourceChanges_%s_%d.jsonl" % (started, target.pid))
            state = await_json(state_path, lambda value: value.get("observerState") == "WATCHING")
            assert "Assets/Python/**/*.py" in state["watchedScopes"] and "Resource/**/*.thm" in state["watchedScopes"], state
            assert state["environment"]["powershellVersion"] and state["environment"]["clrVersion"], state
            assert state["environment"]["processBits"] in (32, 64), state
            print("Observed environment:", json.dumps(state["environment"]))

            # <!-- custom: A duplicate for the same run/root must exit cleanly through the ownership lock instead of creating a second event stream. (ChatGPT-5.6-Sol) -->
            duplicate = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
            duplicate.communicate(timeout=10)
            assert duplicate.returncode == 0

            py = python / "sample.py"
            py.write_text("value = 1\n", encoding="utf-8")
            time.sleep(.05)
            py.write_text("value = 2\n", encoding="utf-8")
            time.sleep(.05)
            py.write_text("value = 3\n", encoding="utf-8")
            (python / "ignored.txt").write_text("not watched\n", encoding="utf-8")
            rows = await_rows(rows_path, 1)
            first = rows[0]
            assert first["path"] == "Assets/Python/sample.py" and first["finalState"] == "PRESENT", first
            assert first["eventCount"] >= 1 and first["engineReloadState"] == "NOT_OBSERVED", first
            assert first["fingerprintStatus"] == "AVAILABLE" and first["fingerprint"] == hashlib.sha256(("value = 3" + os.linesep).encode("utf-8")).hexdigest().upper(), first
            assert all("ignored.txt" not in row["path"] for row in rows), rows

            # <!-- custom: Saving unchanged bytes must still leave disk-event evidence, with the same fingerprint; the watcher must not invent a successful engine reload or a content difference. (GPT-6.1-Sol) -->
            py.write_text("value = 3\n", encoding="utf-8")
            rows = await_rows(rows_path, 2)
            assert rows[1]["path"] == first["path"] and rows[1]["fingerprint"] == first["fingerprint"], rows
            assert rows[1]["engineReloadState"] == "NOT_OBSERVED", rows[1]

            xp = xml / "fixture.xml"
            xp.write_text("<root/>\n", encoding="utf-8")
            rows = await_rows(rows_path, 3)
            assert rows[2]["path"] == "Assets/XML/fixture.xml" and rows[2]["fingerprintStatus"] == "AVAILABLE", rows[2]

            renamed = python / "renamed.py"
            py.rename(renamed)
            rows = await_rows(rows_path, 4)
            assert any(row["path"] == "Assets/Python/renamed.py" and "RENAMED" in row["actionsObserved"] for row in rows), rows

            renamed.unlink()
            rows = await_rows(rows_path, 5)
            assert any(row["path"] == "Assets/Python/renamed.py" and row["finalState"] == "ABSENT" for row in rows), rows

            # <!-- custom: Verify the added map/theme/settings/root-INI scopes and exclusion of unrelated outputs, not just advertised scope strings. (GPT-6.1-Sol) -->
            extra_paths = ("PrivateMaps/test.py", "PrivateMaps/test.CivBeyondSwordWBSave", "Resource/test.thm", "Settings/options.ini", "Settings/CustomDomAdv.txt", "AdvCiv-SAS.ini", "Assets/Config/options.xml")
            for count, relative in enumerate(extra_paths, 6):
                (root / relative).write_text("fixture = 7\n", encoding="utf-8")
                rows = await_rows(rows_path, count)
                assert rows[-1]["path"] == relative and rows[-1]["fingerprintStatus"] == "AVAILABLE", rows[-1]
            (logs / "spam.log").write_text("ignored\n", encoding="utf-8")
            (root / "PrivateMaps/ignored.txt").write_text("ignored\n", encoding="utf-8")
            (root / "Resource/ignored.png").write_bytes(b"ignored")
            time.sleep(2)
            assert len(await_rows(rows_path, 12)) == 12
            trigger.touch()
            target.wait(timeout=10)
            stdout, stderr = watcher.communicate(timeout=15)
            assert watcher.returncode == 0, (stdout, stderr)
            final = await_json(state_path, lambda value: value.get("observerState") == "EXITED")
            assert final["burstsWritten"] >= 5 and final["rawEventsObserved"] >= final["burstsWritten"], final
            assert final["writeFailures"] == 0 and final["rowsDropped"] == 0 and final["watcherErrors"] == 0, final
            print("PASS Runtime source observer: coalescing, Python/XML filters, fingerprints, rename/delete, duplicate ownership and exit")
        finally:
            if target.poll() is None:
                target.terminate()
                target.wait(timeout=10)
            for process in (watcher, duplicate):
                if process is not None and process.poll() is None:
                    process.terminate()
                    process.wait(timeout=10)
        run_exit_subscription_case(root / "subscription-race")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

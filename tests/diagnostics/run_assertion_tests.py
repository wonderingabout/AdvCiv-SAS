# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Manual-only Windows check of the actual assertion diagnostic/policy core with the local Visual C++ Toolkit 2003 (VC2003) compiler.
# Extract production FAssert helpers into a temporary include so startup fallback, cached silent policies, action resolution, dialog context and writer escaping are executed rather than inferred from source spellings. (ChatGPT-5.6-Sol) -->
import argparse
import os
from pathlib import Path
import re
import subprocess
# <!-- custom: Build and execute the extracted assertion core in an isolated temporary workspace so the harness never leaves compiler artifacts in the repository. (ChatGPT-5.6-Sol) -->
import tempfile


ROOT = Path(__file__).resolve().parents[2]


def compiler_environment(args):
    setup = subprocess.run('cmd.exe /d /s /c "call "%s" >nul && set"' % args.vcvars, capture_output=True, text=True, check=True)
    environment = os.environ.copy()
    for line in setup.stdout.splitlines():
        key, separator, value = line.partition("=")
        if separator and key:
            environment[key.upper()] = value
    toolkit = args.compiler.parent.parent
    environment["PATH"] = str(args.compiler.parent) + os.pathsep + environment.get("PATH", "")
    environment["INCLUDE"] = os.pathsep.join((str(toolkit / "include"), str(args.sdk / "include"), environment.get("INCLUDE", "")))
    environment["LIB"] = os.pathsep.join((str(toolkit / "lib"), str(args.sdk / "lib"), environment.get("LIB", "")))
    return environment


def extract_assertion_core(source):
    # <!-- custom: Normalize only the in-memory extraction view so the harness accepts the repository's CRLF source as well as translated text reads. (ChatGPT-5.6-Sol) -->
    source = source.replace("\r\n", "\n").replace("\r", "\n")
    namespace_start = source.index("namespace\n{")
    resource_start = source.index("\n\t// Some Resource IDs", namespace_start)
    core = source[namespace_start:resource_start]
    # <!-- custom: Replace the real modal UI with a controllable fixture while preserving production formatting and the inherited action codes consumed by FAssertDlg. (ChatGPT-5.6-Sol) -->
    dialog_stub = r'''
	DWORD DisplayAssertDialog()
	{
		g_iDialogCount++;
		formatSASAssertionDialogText();
		g_AssertInfo.iSelectedAction = g_iDialogSelectedAction;
		return g_iDialogResult;
	}
} // end anonymous namespace
'''
    exported_start = source.index("// <!-- custom: Cache the optional silent policy", resource_start)
    exported_end = source.index("\n#endif // FASSERT_ENABLE", exported_start)
    return core + dialog_stub + source[exported_start:exported_end] + "\n"


def main():
    program_files = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
    parser = argparse.ArgumentParser(description="Exercise current FAssert logging/silent policy without building or installing the game DLL (Windows, local VC2003 SDK required).")
    parser.add_argument("--compiler", type=Path, default=program_files / "Civ4SDK/Microsoft Visual C++ Toolkit 2003/bin/cl.exe")
    parser.add_argument("--vcvars", type=Path, default=program_files / "Microsoft Visual Studio 10.0/VC/bin/vcvars32.bat")
    parser.add_argument("--sdk", type=Path, default=program_files / "Civ4SDK/WindowsSDK")
    args = parser.parse_args()
    for path in (args.compiler, args.vcvars, args.sdk):
        if not path.exists():
            parser.error("required local compiler/SDK path missing: %s" % path)
    environment = compiler_environment(args)
    source = (ROOT / "CvGameCoreDLL/FAssert.cpp").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="sas-assert-") as directory:
        temporary = Path(directory)
        (temporary / "assertion_under_test.inc").write_text(extract_assertion_core(source), encoding="utf-8")
        executable = temporary / "sas_assertion_harness.exe"
        command = [
            str(args.compiler), "/nologo", "/EHsc", "/MT", "/W4", "/WX",
            "/I" + str(temporary), "/I" + str(ROOT / "CvGameCoreDLL"),
            str(ROOT / "tests/diagnostics/sas_assertion_harness.cpp"),
            "/Fo" + str(temporary / "sas_assertion_harness.obj"), "/Fe" + str(executable),
        ]
        compiled = subprocess.run(command, cwd=temporary, env=environment, capture_output=True, text=True)
        if compiled.stdout or compiled.stderr:
            print(compiled.stdout + compiled.stderr, end="")
        if compiled.returncode:
            return compiled.returncode
        output_root = temporary / "unicode_é"
        output_root.mkdir()
        executed = subprocess.run([str(executable), str(output_root)], cwd=temporary, env=environment)
        if executed.returncode:
            raise RuntimeError("assertion harness failed with exit code %d" % executed.returncode)
        logs = sorted((output_root / "Logs").glob("SASAssertions_*.log"))
        if len(logs) != 6 or any("_pid" in log.name for log in logs):
            raise RuntimeError("expected lazy startup/menu1/new1/menu2/load2/load4 assertion logs, got %s" % [log.name for log in logs])
        by_context = {}
        for log in logs:
            rows = log.read_bytes().splitlines()
            if not rows or b"record=SAS_ASSERT_METADATA" not in rows[0]:
                raise RuntimeError("missing leading assertion metadata row: %s" % log.name)
            match = re.search(rb" session=([^ ]+)", rows[0])
            if not match:
                raise RuntimeError("metadata session identity missing: %s" % log.name)
            context = match.group(1).decode("ascii")
            by_context[context] = rows
            if ("_%s.log" % context) not in log.name:
                raise RuntimeError("filename/session mismatch: %s vs %s" % (log.name, context))
            if b"assertionsEnabled=1" not in rows[0] or b"fassertEnabled=1" not in rows[0] or b"build=HARNESS" not in rows[0]:
                raise RuntimeError("build/assertion metadata missing: %s" % log.name)
            if b"writer=OPEN_APPEND_CLOSE liveReadable=1 forcedPhysicalFlush=0" not in rows[0]:
                raise RuntimeError("writer semantics missing from metadata: %s" % log.name)
        expected_contexts = {"startup", "menu1", "new1", "menu2", "load2", "load4"}
        if set(by_context) != expected_contexts:
            raise RuntimeError("unexpected assertion session contexts: %s" % sorted(by_context))
        if "new3" in by_context:
            raise RuntimeError("quiet new3 session created an assertion file")
        startup_rows = by_context["startup"]
        menu1_rows = by_context["menu1"]
        new_rows = by_context["new1"]
        menu2_rows = by_context["menu2"]
        load_rows = by_context["load2"]
        load4_rows = by_context["load4"]
        counts = {context: len(by_context[context]) for context in sorted(by_context)}
        if counts != {"load2": 3, "load4": 3, "menu1": 3, "menu2": 3, "new1": 13, "startup": 3}:
            raise RuntimeError("unexpected metadata/pair row counts: %s" % counts)
        ordered_contexts = ("startup", "menu1", "new1", "menu2", "load2", "load4")
        all_event_rows = []
        for context in ordered_contexts:
            all_event_rows.extend(by_context[context][1:])
        pairs = list(zip(all_event_rows[0::2], all_event_rows[1::2]))
        if len(pairs) != 11:
            raise RuntimeError("expected eleven failure/choice pairs, got %d" % len(pairs))
        for index, (failure, choice) in enumerate(pairs, 1):
            if b"record=SAS_ASSERT_FAILURE" not in failure or b"record=SAS_ASSERT_CHOICE" not in choice:
                raise RuntimeError("broken failure/choice pair %d" % index)
            if ("assertion=%d" % index).encode("ascii") not in failure or ("assertion=%d" % index).encode("ascii") not in choice:
                raise RuntimeError("broken process-wide assertion sequence %d" % index)
        if b"sessionSequence=0" not in startup_rows[0] or b"initialSilentMode=-1 initialSilentPolicy=STARTUP_DIALOG" not in startup_rows[0]:
            raise RuntimeError("startup metadata mismatch")
        expected_sequences = {"startup": 0, "menu1": 1, "new1": 1, "menu2": 2, "load2": 2, "load4": 4}
        for context, sequence in expected_sequences.items():
            rows = by_context[context]
            if (" session=%s sessionSequence=%d" % (context, sequence)).encode("ascii") not in rows[0]:
                raise RuntimeError("metadata sequence mismatch for %s" % context)
            marker = (" session=%s sessionSequence=%d" % (context, sequence)).encode("ascii")
            for row in rows[1:]:
                if marker not in row:
                    raise RuntimeError("event row lost session identity for %s" % context)
        if b"silentMode=-1 silentPolicy=STARTUP_DIALOG" not in pairs[0][0] or b"choice=IGNORE_ONCE action=IGNORE_ONCE automatic=0" not in pairs[0][1]:
            raise RuntimeError("startup assertion did not retain the normal dialog")
        if b"session=menu1 sessionSequence=1" not in pairs[1][0] or b"choice=AUTOMATIC action=IGNORE_ONCE automatic=1" not in pairs[1][1]:
            raise RuntimeError("first main-menu visit did not use menu1 with cached Ignore Once")
        if b"silentMode=1 silentPolicy=IGNORE_ONCE" not in pairs[2][0] or b"choice=AUTOMATIC action=IGNORE_ONCE automatic=1" not in pairs[2][1]:
            raise RuntimeError("cached Ignore Once policy did not apply automatically")
        if b"silentMode=2 silentPolicy=IGNORE_ALWAYS" not in pairs[3][0] or b"action=IGNORE_ALWAYS automatic=1" not in pairs[3][1]:
            raise RuntimeError("automatic Ignore Always policy mismatch")
        if b"silentMode=3 silentPolicy=STOP_AUTO_PLAY" not in pairs[4][0] or b"action=IGNORE_ONCE automatic=1 silentFallback=AUTOPLAY_INACTIVE" not in pairs[4][1]:
            raise RuntimeError("inactive-autoplay Stop policy fallback mismatch")
        if b"action=STOP_AUTO_PLAY automatic=1 silentFallback=-" not in pairs[5][1]:
            raise RuntimeError("active-autoplay Stop policy mismatch")
        if b"silentMode=9 silentPolicy=DIALOG_INVALID" not in pairs[6][0] or b"automatic=0" not in pairs[6][1] or b"dialogShown=1" not in pairs[6][1]:
            raise RuntimeError("invalid policy did not return to the dialog")
        for row in pairs[2][0], pairs[2][1], pairs[6][0], pairs[6][1], pairs[9][0], pairs[9][1], pairs[10][0], pairs[10][1]:
            if b"turn=53 elapsed=24" not in row or b"activePlayer=4 activeTeam=2" not in row:
                raise RuntimeError("initialized assertion context missing")
        for row in pairs[7]:
            if len(row) >= 16384 or b"rowTruncated=1" not in row or b"\\x01" not in row:
                raise RuntimeError("escaped-field truncation contract failed")
            for field in (b"file", b"function", b"expression", b"message"):
                if not re.search(field + rb'="(?:[^"\\]|\\.)*"', row):
                    raise RuntimeError("truncated quoted field was not closed: %s" % field.decode("ascii"))
        if b"session=menu2 sessionSequence=2" not in pairs[8][0]:
            raise RuntimeError("second main-menu visit did not advance only the menu counter")
        if b"session=load2 sessionSequence=2" not in pairs[9][0]:
            raise RuntimeError("menu visits consumed the new/load game counter")
        if b"session=load4 sessionSequence=4" not in pairs[10][0]:
            raise RuntimeError("quiet new3 session did not advance numbering before load4")
        print("PASS C++ assertion diagnostics: startup/menu/new/load rollover, separate menu/game counters, lazy numbering/files, process-wide sequence, cached policies, automatic/fallback actions, shared dialog/log context, Unicode path and escaped-row bounds")
    print("No game DLL or project intermediates were changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

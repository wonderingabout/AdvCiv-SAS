#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Until 2026-11-18 three Pythons were installed, and `python` (3.12) and `py` (3.14) started different ones, so a package installed for one was missing from the other; the transcript search under `py` read 3 of 222 Codex logs.
# After moving to one Python, the user asked how we would know when to move again: this reports what is installed, what is newest, and whether every package the helpers import is ready for the newest Python, as 3.15 waited on PyYAML in November 2026.
# It reads python.org's and PyPI's public JSON and changes nothing; "compatible wheel available" means pip will not need a compiler, not that the helpers were tested on that Python. (Claude code Opus 5.5) -->

# <!-- custom: json and urllib read the release lists; shutil and subprocess find which Python py and python start; sys gives the running version. (Claude code Opus 5.5) -->
import json
import shutil
import subprocess
import sys
import urllib.request

# <!-- custom: The packages the helpers import, by PyPI name; zstandard is left out, as Python 3.14 reads zstd itself.
# Add one here when a helper starts importing it. (Claude code Opus 5.5) -->
REQUIRED = ("pillow", "pyffi", "setuptools", "numpy", "pyte", "scipy", "pyyaml")


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "python-versions-check"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def version_key(name):
    return tuple(int(part) for part in name.split()[-1].split("."))


def stable_releases():
    releases = fetch("https://www.python.org/api/v2/downloads/release/?is_published=true&pre_release=false")
    return sorted((r["name"] for r in releases if r["name"].startswith("Python 3.")), key=version_key, reverse=True)


def started_by(command):
    path = shutil.which(command)
    if not path:
        return "not found"
    result = subprocess.run([path, "-c", "import sys; print(sys.version.split()[0], sys.executable)"], capture_output=True, text=True)
    return result.stdout.strip() or (result.stderr.strip().splitlines() or ["no answer"])[-1]


def wheel_fits(filename, minor):
    # <!-- custom: A wheel's name ends in python-abi-platform tags, each possibly a dotted list (PyPA's platform compatibility tags).
    # Codex's 2026-11-18 review showed the first rule, matching "abi3" or "none-any" anywhere in the name, took a Linux-only abi3 wheel or a Python 2 pure wheel as ready for Windows CPython 3.15; all three parts must fit now. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
    parts = filename[:-len(".whl")].split("-")
    if len(parts) < 5:
        return False
    target = int(minor.split(".")[1])
    pythons, abis, platforms = parts[-3].split("."), parts[-2].split("."), parts[-1].split(".")
    if not ({"win_amd64", "any"} & set(platforms)):
        return False
    for python in pythons:
        for abi in abis:
            if python == "cp3%d" % target and abi in ("cp3%d" % target, "abi3", "none"):
                return True
            if python.startswith("cp3") and python[3:].isdigit() and int(python[3:]) <= target and abi == "abi3":
                return True
            if python in ("py3", "py3%d" % target) and abi == "none":
                return True
    return False


def requires_python_allows(spec, version):
    # <!-- custom: A file's Requires-Python can exclude the new Python even when its tags fit, as Codex's review pointed out; pip's own vendored packaging library reads the specifier. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
    if not spec:
        return True
    # <!-- custom: The packaging library when installed, otherwise the copy pip carries, so no extra package is needed. (Claude code Opus 5.5) -->
    try:
        from packaging.specifiers import SpecifierSet
    except ImportError:
        from pip._vendor.packaging.specifiers import SpecifierSet
    return SpecifierSet(spec).contains(version, prereleases=True)


def package_ready(package, minor, version):
    data = fetch("https://pypi.org/pypi/%s/json" % package)
    files = [f for f in data["urls"] if f["filename"].endswith(".whl") and not f.get("yanked")]
    ready = any(wheel_fits(f["filename"], minor) and requires_python_allows(f.get("requires_python"), version) for f in files)
    return data["info"]["version"], ready


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    launcher = subprocess.run(["py", "-0p"], capture_output=True, text=True).stdout.strip()
    print("Installed (py -0p):")
    print(launcher or "  the py launcher is missing")
    print("python starts: %s" % started_by("python"))
    print("py starts:     %s" % started_by("py"))
    releases = stable_releases()
    newest = releases[0].split()[-1]
    newest_minor = ".".join(newest.split(".")[:2])
    print("Newest Python on python.org: %s" % newest)
    installed = [line.split()[0].lstrip("-V:").rstrip("*") for line in launcher.splitlines() if line.strip().startswith("-V:3.")]
    for minor in sorted(set(".".join(v.split(".")[:2]) for v in installed)):
        latest = next((r.split()[-1] for r in releases if r.split()[-1].startswith(minor + ".")), "?")
        print("Newest %s release: %s" % (minor, latest))
    print("Packages the helpers import, for Python %s on 64-bit Windows:" % newest_minor)
    waiting = []
    for package in REQUIRED:
        version, ready = package_ready(package, newest_minor, newest)
        print("  %-11s %-8s %s" % (package, version, "compatible wheel available" if ready else "NO compatible wheel"))
        if not ready:
            waiting.append(package)
    if waiting:
        print("Python %s waits on: %s" % (newest_minor, ", ".join(waiting)))
    else:
        print("Every package has a compatible wheel for Python %s; installing them and rerunning the helpers that use them is still the real test" % newest_minor)


if __name__ == "__main__":
    main()

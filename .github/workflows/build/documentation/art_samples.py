#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: The Art Tools Guide's sample pictures fell behind the renderer once: Grace's still kept the wide eyes of a render made before the bone skinning was fixed, while her GIFs had them right.
# CI cannot render them, since it has no Civ4 art, so LLM_Helpers/regenerate_art_samples.py records a fingerprint of the renderer's code after a full run, and this check fails when that code has changed since.
# Comments are left out of the fingerprint, so editing only comments does not ask for new pictures. (Claude code Opus 5.5) -->

# <!-- custom: argparse parses the options; hashlib computes the fingerprint; io and tokenize read code without its comments; json stores the fingerprint; pathlib finds the files. (Claude code Opus 5.5) -->
import argparse
import hashlib
import io
import json
from pathlib import Path
import tokenize

ROOT = Path(__file__).resolve().parents[4]
FINGERPRINT = "LLM_Helpers/art_samples_fingerprint.json"
# <!-- custom: The scripts whose code decides what the samples look like, including the sample list itself. (Claude code Opus 5.5) -->
RENDERER_FILES = ("LLM_Helpers/nif_preview.py", "LLM_Helpers/civ4_assets.py", "LLM_Helpers/fpk_tool.py", "LLM_Helpers/plot_scene.py", "LLM_Helpers/art_gallery.py", "LLM_Helpers/art_search.py", "LLM_Helpers/regenerate_art_samples.py")


def code_tokens(text):
    # <!-- custom: The file's tokens without comments and blank-line breaks, so a comment edit or a reflow leaves the fingerprint unchanged. (Claude code Opus 5.5) -->
    skipped = (tokenize.COMMENT, tokenize.NL, tokenize.ENCODING)
    return "\n".join("%d %s" % (token.type, token.string) for token in tokenize.generate_tokens(io.StringIO(text).readline) if token.type not in skipped)


def fingerprint(root=ROOT):
    digest = hashlib.sha256()
    for name in RENDERER_FILES:
        digest.update(name.encode("utf-8"))
        digest.update(code_tokens((root / name).read_text(encoding="utf-8")).encode("utf-8"))
    return digest.hexdigest()


def write(root=ROOT):
    (root / FINGERPRINT).write_text(json.dumps({"fingerprint": fingerprint(root), "files": list(RENDERER_FILES)}, indent=1) + "\n", encoding="utf-8")


def check(root=ROOT):
    path = root / FINGERPRINT
    if not path.is_file():
        return ["%s is missing; run python LLM_Helpers/regenerate_art_samples.py" % FINGERPRINT]
    if json.loads(path.read_text(encoding="utf-8")).get("fingerprint") != fingerprint(root):
        return ["renderer code changed since the art samples were last regenerated (%s); run python LLM_Helpers/regenerate_art_samples.py, review the pictures in _1_AdvCiv-SAS/Images/LLM, and commit them with the updated %s" % (", ".join(RENDERER_FILES), FINGERPRINT)]
    return []


def main():
    parser = argparse.ArgumentParser(description="Check that the Art Tools Guide's rendered samples were regenerated after the renderer's code last changed.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = check(args.repo_root)
    print("FAIL art sample freshness" if errors else "PASS art sample freshness")
    for error in errors:
        print("  - " + error)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())

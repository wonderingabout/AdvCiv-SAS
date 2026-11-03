#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: a religion's TechButton and GenericTechButton show its founding
# tech's picture.
#
# <!-- custom: The choose-tech popup and the top tech bar show a religion's TechButton instead of its founding tech's button while the religion is unfounded.
# BtS drew each religion's TechButton as its BtS founding tech's picture plus a religion badge, so moving a religion to another tech without updating them showed e.g. Polytheism's marble heads on Calendar.
# Each button must therefore be the founding tech's own Button, or a BtS religion button whose drawn tech is still the founding tech. See KI#1072.2. (Claude code Opus 5.5) -->

from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

# <!-- custom: Resolve the shared XML helpers from this subject subfolder like the other build/xml checks. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from xml_defines import get_default_repo_root, local_name, child_text_by_local_name


TECH_INFOS_REL_PATH = Path("Assets/XML/Technologies/CIV4TechInfos.xml")
RELIGION_INFOS_REL_PATH = Path("Assets/XML/GameInfo/CIV4ReligionInfo.xml")
BUTTON_TAGS = ("TechButton", "GenericTechButton")
# <!-- custom: The founding tech each BtS religion button picture was drawn for, from BtS's own CIV4ReligionInfo.xml. (Claude code Opus 5.5) -->
BTS_RELIGION_BUTTON_TECHS = {
	"Buddhism.dds": "TECH_MEDITATION",
	"Christianity.dds": "TECH_THEOLOGY",
	"Confucianism.dds": "TECH_CODE_OF_LAWS",
	"Hinduism.dds": "TECH_POLYTHEISM",
	"Islam.dds": "TECH_DIVINE_RIGHT",
	"Judaism.dds": "TECH_MONOTHEISM",
	"Taoism.dds": "TECH_PHILOSOPHY",
}


def infos(repo_root: Path, rel_path: Path, info_tag: str) -> list[ET.Element]:
	path = repo_root / rel_path
	if not path.exists():
		raise RuntimeError(f"missing file: {path}")
	return [node for node in ET.parse(path).getroot().iter() if local_name(node.tag) == info_tag]


def button_file(button: str) -> str:
	# <!-- custom: BtS button strings are ",<file>,<atlas>,x,y"; SAS art can be a plain path.
	# Return the picture's file name. (Claude code Opus 5.5) -->
	parts = [part for part in button.split(",") if part.strip()]
	return parts[0].strip().replace("\\", "/").split("/")[-1] if parts else ""


def check_religion_tech_buttons(repo_root: Path) -> list[str]:
	tech_buttons = {child_text_by_local_name(node, "Type"): (child_text_by_local_name(node, "Button") or "").strip() for node in infos(repo_root, TECH_INFOS_REL_PATH, "TechInfo")}
	failures: list[str] = []
	for node in infos(repo_root, RELIGION_INFOS_REL_PATH, "ReligionInfo"):
		religion = child_text_by_local_name(node, "Type")
		tech = child_text_by_local_name(node, "TechPrereq")
		if tech not in tech_buttons:
			failures.append(f"{religion}: TechPrereq {tech!r} is not a tech")
			continue
		for tag in BUTTON_TAGS:
			button = (child_text_by_local_name(node, tag) or "").strip()
			if button == tech_buttons[tech]:
				continue
			drawn_for = BTS_RELIGION_BUTTON_TECHS.get(button_file(button))
			if drawn_for == tech:
				continue
			if drawn_for is not None:
				failures.append(f"{religion}: {tag} is the BtS {button_file(button)} picture drawn for {drawn_for}, but {religion} is founded by {tech}; use {tech}'s Button")
			else:
				failures.append(f"{religion}: {tag} {button_file(button)!r} is neither {tech}'s Button nor a BtS religion button drawn for {tech}")
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that religion tech buttons show their founding tech's picture.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root(), help="repository root; defaults to the root containing .github/")
	args = parser.parse_args()
	try:
		failures = check_religion_tech_buttons(args.repo_root)
	except RuntimeError as exc:
		failures = [str(exc)]
	if failures:
		print("FAIL religion tech buttons")
		for failure in failures:
			print(f"  - {failure}")
		return 1
	print("PASS religion tech buttons")
	return 0


if __name__ == "__main__":
	sys.exit(main())

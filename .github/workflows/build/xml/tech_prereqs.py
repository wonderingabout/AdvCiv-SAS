#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: every tech prerequisite names an existing tech in an earlier
# tech-tree column, and the prerequisite graph has no cycle.
#
# <!-- custom: KI#29's tech-advisor crash on Transhumanism's box was recalled as coming from placeholder prerequisites that formed an impossible or circular dependency.
# A prerequisite drawn in the same or a later iGridX column would also point the tech-tree arrow backward. See KI#29. (Claude code Opus 5.5) -->

from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

# <!-- custom: Resolve the shared XML helpers from this subject subfolder like the other build/xml checks. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from xml_defines import get_default_repo_root, local_name, child_text_by_local_name


TECH_INFOS_REL_PATH = Path("Assets/XML/Technologies/CIV4TechInfos.xml")
PREREQ_LIST_TAGS = ("OrPreReqs", "AndPreReqs")


def read_techs(repo_root: Path) -> dict[str, tuple[int, list[str]]]:
	path = repo_root / TECH_INFOS_REL_PATH
	if not path.exists():
		raise RuntimeError(f"missing file: {path}")
	techs: dict[str, tuple[int, list[str]]] = {}
	for node in ET.parse(path).getroot().iter():
		if local_name(node.tag) != "TechInfo":
			continue
		tech_type = child_text_by_local_name(node, "Type")
		if tech_type is None:
			continue
		grid_x_text = child_text_by_local_name(node, "iGridX")
		try:
			grid_x = int(grid_x_text or "")
		except ValueError as exc:
			raise RuntimeError(f"{TECH_INFOS_REL_PATH}: {tech_type} has invalid iGridX {grid_x_text!r}") from exc
		prereqs: list[str] = []
		for child in node:
			if local_name(child.tag) in PREREQ_LIST_TAGS:
				prereqs.extend((item.text or "").strip() for item in child.iter() if item is not child and (item.text or "").strip())
		techs[tech_type] = (grid_x, prereqs)
	return techs


def find_cycle(techs: dict[str, tuple[int, list[str]]]) -> list[str]:
	# <!-- custom: Iterative depth-first search; returns one cycle as a tech path, or an empty list. (Claude code Opus 5.5) -->
	state: dict[str, int] = {}
	for root in techs:
		if root in state:
			continue
		stack = [(root, iter(techs[root][1]))]
		path = [root]
		state[root] = 1
		while stack:
			tech, children = stack[-1]
			child = next(children, None)
			if child is None:
				state[tech] = 2
				stack.pop()
				path.pop()
				continue
			if child not in techs:
				continue
			if state.get(child) == 1:
				return path[path.index(child):] + [child]
			if child not in state:
				state[child] = 1
				stack.append((child, iter(techs[child][1])))
				path.append(child)
	return []


def check_tech_prereqs(repo_root: Path) -> list[str]:
	techs = read_techs(repo_root)
	failures: list[str] = []
	for tech_type, (grid_x, prereqs) in techs.items():
		for prereq in prereqs:
			if prereq not in techs:
				failures.append(f"{tech_type} requires {prereq}, which is not a tech")
			elif techs[prereq][0] >= grid_x:
				failures.append(f"{tech_type} (iGridX={grid_x}) requires {prereq} (iGridX={techs[prereq][0]}), which is not in an earlier column")
	cycle = find_cycle(techs)
	if cycle:
		failures.append("circular prerequisites: " + " -> ".join(cycle))
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that tech prerequisites exist, sit in earlier columns and form no cycle.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root(), help="repository root; defaults to the root containing .github/")
	args = parser.parse_args()
	try:
		failures = check_tech_prereqs(args.repo_root)
	except RuntimeError as exc:
		failures = [str(exc)]
	if failures:
		print("FAIL tech prerequisites")
		for failure in failures:
			print(f"  - {failure}")
		return 1
	print("PASS tech prerequisites")
	return 0


if __name__ == "__main__":
	sys.exit(main())

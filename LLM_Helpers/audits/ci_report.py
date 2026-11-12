#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Collects every CI failure into one text file, from a local run of the workflows' own steps or from GitHub's results for a commit, so one pass can fix them all rather than one push per failure.
# Agents each rebuilt a throwaway runner for this; the steps are read from the workflows, so a new check needs no change here.
# See LLM_Helpers/README.md. (Claude code Opus 5.5) -->

# <!-- custom: argparse parses the options; concurrent.futures runs steps in parallel; json writes the event file and reads GitHub's answers; os, shutil, subprocess and tempfile run the steps; pathlib finds the repository; sys reports errors. (Claude code Opus 5.5) -->
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
# <!-- custom: re reads the workflows' expressions and the remote. (Claude code Opus 5.5) -->
import re
import shutil
import subprocess
import sys
import tempfile

# <!-- custom: PyYAML reads the workflows; fail with the install command if it is missing. (Claude code Opus 5.5) -->
try:
	import yaml
except ImportError:
	raise SystemExit("PyYAML is required: py -m pip install pyyaml")

# <!-- custom: Helpers now sit in LLM_Helpers folders named by job, so find the repo root from the LLM_Helpers folder instead of a fixed parent depth. (Claude code Opus 5.5) -->
REPO = next(path for path in Path(__file__).resolve().parents if path.name == "LLM_Helpers").parent
DEFAULT_OUT = REPO / "LLM_Helpers" / "outputs" / "ci_report.txt"
# <!-- custom: Not run locally: the predump workflow refreshes a file and opens a PR rather than checking, and the Python 2.4 workflow needs Docker, for which NATIVE_STEPS runs the same check. (Claude code Opus 5.5) -->
NOT_RUN = ("runtime-aip-predump-refresh.yml", "python24-compile.yml")
PYTHON24 = Path(r"C:\Python24\python.exe")
# <!-- custom: The checks of shipped diagnostic and hands-free defaults read staged content here, as development values usually stay enabled and unstaged. (Claude code Opus 5.5) -->
STAGED_CHECKS = re.compile(r"(build/(?:diagnostics/(?:bbai_log|runtime_status|sas_game_record_log)|runtime/hands_free_defaults)\.py)")
LOG_LINES = 200
PLACEHOLDER_MESSAGE = "Local CI candidate (no commit message given)\n"


def git(*args):
	return subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=REPO).stdout.strip()


def default_base():
	# <!-- custom: The base GitHub would compare with: the upstream commit when HEAD differs from it, which after an amend is the commit being replaced, else the parent.
	# Comparing an amended commit with its parent passed locally on 2026-11-09, as plot_scene.py was new there, while GitHub, comparing with the replaced commit, failed a changed signature. (Claude code Opus 5.5) -->
	upstream = git("rev-parse", "--verify", "-q", "@{u}")
	head = git("rev-parse", "HEAD")
	if upstream and upstream != head:
		return upstream
	# <!-- custom: When HEAD is already pushed and the working tree holds the next commit's edits, GitHub will compare that commit with HEAD, not with HEAD's parent.
	# On 2026-11-12 the parent mixed the pushed commit's changes into an uncommitted candidate's report; the parent stays the base only for rechecking a clean, pushed HEAD. (Claude code Opus 5.5) -->
	if upstream and git("status", "--porcelain", "--untracked-files=no"):
		return head
	return git("rev-parse", "HEAD~1")


def bash_program():
	# <!-- custom: Git Bash first: on Windows a bare "bash" may be WSL's, which cannot see this Python or these paths. (Claude code Opus 5.5) -->
	git_bash = Path(r"C:\Program Files\Git\bin\bash.exe")
	return str(git_bash) if git_bash.exists() else shutil.which("bash")


def workflow_steps(expressions):
	# <!-- custom: Each run: step of the workflows, with the GitHub expressions they use filled in; steps that only install or check out are uses: steps and need nothing here. (Claude code Opus 5.5) -->
	def expand(text):
		return re.sub(r"\$\{\{(.*?)\}\}", lambda match: expressions.get(match.group(1).strip(), ""), str(text))
	steps = []
	for path in sorted((REPO / ".github" / "workflows").glob("*.yml")):
		if path.name in NOT_RUN:
			continue
		workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
		for job in workflow["jobs"].values():
			env = {key: expand(value) for key, value in {**(workflow.get("env") or {}), **(job.get("env") or {})}.items()}
			for step in job["steps"]:
				if "run" in step:
					steps.append((path.name, step.get("name", step["run"][:60]), expand(step["run"]), {**env, **{key: expand(value) for key, value in (step.get("env") or {}).items()}}))
	return steps


def native_steps():
	# <!-- custom: The two checks GitHub runs through an action or Docker image, run here by their local tools; a tool that is absent is listed as not covered rather than passing silently. (Claude code Opus 5.5) -->
	steps, missing = [], []
	if shutil.which("npx"):
		steps.append(("documentation-markdownlint.yml", "Check maintained Markdown", "npx markdownlint-cli2@0.23.2", {}))
	else:
		missing.append("markdownlint: Node.js is not installed")
	if PYTHON24.exists():
		steps.append(("python24-compile.yml", "Compile-check with CPython 2.4", '"%s" .github/workflows/build/python/python24_compile.py --repo-root .' % PYTHON24.as_posix(), {}))
	else:
		missing.append("Python 2.4 compile: %s is not installed" % PYTHON24)
	return steps, missing


def run_step(step, shared_env, bash):
	workflow, name, command, env = step
	script = 'command -v ruff >/dev/null || ruff() { py -m ruff "$@"; }\nset -e\n' + STAGED_CHECKS.sub(r"\1 --staged", command)
	with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False, encoding="utf-8", newline="\n") as handle:
		handle.write(script)
	try:
		result = subprocess.run([bash, handle.name], capture_output=True, text=True, encoding="utf-8", errors="replace", env={**os.environ, **shared_env, **{key: str(value) for key, value in env.items()}}, cwd=REPO, timeout=900)
		return step, result.returncode, result.stdout + result.stderr
	except subprocess.TimeoutExpired:
		return step, 124, "timed out after 900 s"
	finally:
		os.unlink(handle.name)


def tail(text):
	lines = text.strip().splitlines()
	return "\n".join((["[... %d earlier lines omitted]" % (len(lines) - LOG_LINES)] if len(lines) > LOG_LINES else []) + lines[-LOG_LINES:])


def candidate_commit(message):
	# <!-- custom: Eight checks judge the commits of a push, not the files on disk: the SASGameRecord and Runtime revision checks, the commit-reference check, the four DLL checks and the KI title check.
	# So before a commit they had nothing new to judge and passed silently: on 2026-11-12 a local run passed while GitHub failed the commit that followed, as map_preview_dds.py had begun reading SGR rows without the SAS_SGR_REVISION bump the rule asks for.
	# The staged files become a temporary commit on top of HEAD, made with git commit-tree, which records a commit object without moving any branch or touching the working tree; it is passed to the checks as the pushed commit. (Claude code Opus 5.5) -->
	tree = git("write-tree")
	result = subprocess.run(["git", "commit-tree", tree, "-p", "HEAD"], input=message, capture_output=True, text=True, encoding="utf-8", cwd=REPO)
	if result.returncode:
		raise SystemExit("could not make the candidate commit: %s" % result.stderr.strip())
	return result.stdout.strip()


def local_report(args):
	head = git("rev-parse", "HEAD")
	base = git("rev-parse", args.base) if args.base else default_base()
	# <!-- custom: Staged changes are the next commit, so the commit checks judge them as one; unstaged development values stay out, as they would from the real commit. (Claude code Opus 5.5) -->
	staged = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO).returncode != 0
	if staged:
		message = args.message.read_text(encoding="utf-8") if args.message else PLACEHOLDER_MESSAGE
		head = candidate_commit(message)
	else:
		message = git("log", "-1", "--format=%B")
	commits = git("rev-list", "--reverse", "%s..%s" % (base, head)).split() or [head]
	expressions = {"github.event_name": "push", "github.event.pull_request.base.sha || github.event.before": base, "github.event.before": base, "github.sha": head, "github.ref_name": "main", "github.event.repository.default_branch": "main", "github.ref": "refs/heads/main", "github.workspace": REPO.as_posix()}
	with tempfile.TemporaryDirectory() as folder:
		event_path = Path(folder) / "event.json"
		# <!-- custom: The push event's fields the checks read; without a real file six of them failed with Permission denied. (Claude code Opus 5.5) -->
		event_path.write_text(json.dumps({"before": base, "after": head, "ref": "refs/heads/main", "forced": False, "head_commit": {"id": head, "message": message}, "commits": [{"id": commit, "message": git("log", "-1", "--format=%B", commit)} for commit in commits], "repository": {"default_branch": "main"}}), encoding="utf-8")
		shared_env = {"GITHUB_SHA": head, "GITHUB_EVENT_NAME": "push", "GITHUB_REF_NAME": "main", "GITHUB_WORKSPACE": str(REPO), "GITHUB_EVENT_PATH": str(event_path), "GITHUB_OUTPUT": os.devnull, "GITHUB_STEP_SUMMARY": os.devnull, "PYTHONIOENCODING": "utf-8"}
		native, missing = native_steps()
		steps = workflow_steps(expressions) + native
		bash = bash_program()
		with ThreadPoolExecutor(args.jobs) as pool:
			results = list(pool.map(lambda step: run_step(step, shared_env, bash), steps))
	failures = [result for result in results if result[1]]
	if staged:
		judged = "Staged changes judged as a temporary commit %s on HEAD, compared with %s, with %s." % (head[:12], base[:12], "the message from %s" % args.message if args.message else "a placeholder message, so the title and Update DLL checks may fail: pass --message with the draft")
	else:
		judged = "Nothing staged, so the commit checks judge HEAD %s, compared with %s; stage the candidate for them to judge it." % (head[:12], base[:12])
	lines = ["Local CI report: %d of %d steps failed" % (len(failures), len(results)), judged, "Other checks read the working tree, unstaged development values included."]
	lines += ["Not covered: %s" % item for item in [*NOT_RUN[:1], *missing]]
	for (workflow, name, command, _), code, output in failures:
		lines += ["", "=" * 8 + " FAIL %s: %s (exit %d)" % (workflow, name, code), command.strip()[:300], "-" * 8, tail(output)]
	return lines, bool(failures)


def api_get(url):
	# <!-- custom: Through curl, which uses the system's certificates: Python's urllib failed here with CERTIFICATE_VERIFY_FAILED, and turning verification off is no fix. (Claude code Opus 5.5) -->
	result = subprocess.run(["curl", "-sSfL", "-H", "User-Agent: advciv-sas-ci-report", "-H", "Accept: application/vnd.github+json", url], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90)
	if result.returncode:
		raise SystemExit("GitHub API request failed: %s" % result.stderr.strip())
	return json.loads(result.stdout)


def github_report(args):
	# <!-- custom: Reads GitHub's results for a commit: which workflows and steps failed comes from the public API, and their logs from the gh command when it is logged in, as GitHub gives logs only to signed-in users. (Claude code Opus 5.5) -->
	match = re.search(r"github\.com[:/](.+?)(?:\.git)?$", git("remote", "get-url", "origin"))
	if not match:
		raise SystemExit("origin is not a GitHub remote")
	slug = match.group(1)
	sha = git("rev-parse", args.sha or "HEAD")
	runs = api_get("https://api.github.com/repos/%s/actions/runs?head_sha=%s&per_page=100" % (slug, sha))["workflow_runs"]
	if not runs:
		raise SystemExit("GitHub has no workflow runs for %s; has it been pushed?" % sha[:12])
	signed_in = bool(shutil.which("gh")) and subprocess.run(["gh", "auth", "status"], capture_output=True).returncode == 0
	unfinished = [run["name"] for run in runs if run["status"] != "completed"]
	failed = [run for run in runs if run["conclusion"] not in ("success", "skipped", None)]
	lines = ["GitHub CI report: %d of %d workflows failed" % (len(failed), len(runs)), "Commit %s" % sha[:12]]
	if unfinished:
		lines.append("Still running, so this report is partial: %s" % ", ".join(unfinished))
	if failed and not signed_in:
		lines.append("Step names only: for the failure text, log in once with: gh auth login")
	for run in failed:
		lines += ["", "=" * 8 + " FAIL %s: %s" % (run["name"], run["html_url"])]
		for job in api_get(run["jobs_url"] + "?per_page=100")["jobs"]:
			lines += ["  failed step: %s" % step["name"] for step in job["steps"] if step.get("conclusion") == "failure"]
		if signed_in:
			logs = subprocess.run(["gh", "run", "view", str(run["id"]), "--repo", slug, "--log-failed"], capture_output=True, text=True, encoding="utf-8", errors="replace")
			lines += ["-" * 8, tail(logs.stdout + logs.stderr)]
	return lines, bool(failed or unfinished)


def main():
	parser = argparse.ArgumentParser(description="Collect every CI failure into one text file, from a local run of the workflows or from GitHub's results.")
	parser.add_argument("source", nargs="?", choices=("local", "github"), default="local", help="run the workflows' steps here, or read GitHub's results (default: local)")
	parser.add_argument("--base", help="local: the commit to compare with (default: what GitHub would use)")
	parser.add_argument("--message", type=Path, help="local: a file with the draft commit message, used for the staged candidate commit")
	parser.add_argument("--sha", help="github: the commit to read (default: HEAD)")
	parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="report file (default: LLM_Helpers/outputs/ci_report.txt, Git-ignored)")
	parser.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) // 2))
	args = parser.parse_args()
	lines, failed = (github_report if args.source == "github" else local_report)(args)
	args.out.parent.mkdir(parents=True, exist_ok=True)
	args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
	print("\n".join(lines[:4]))
	print("wrote %s" % args.out)
	return 1 if failed else 0


if __name__ == "__main__":
	sys.exit(main())

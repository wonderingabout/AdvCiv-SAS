#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Prints what the user did in Git Bash (MINGW64, in a mintty window) since a given time: by default the commands, from the record ~/.bashrc writes; with --output, the windows' full text, from the logs ~/.minttyrc writes.
# Agents' own apps show only the commands they run themselves, so this is how they see the user's amends, pushes and force-pushes; on 2026-11-17 an agent told the user to force-push what the user had already pushed.
# The command record alone left out Git's answers, such as line-ending warnings or a push's "(forced update)" line, which say what really happened, so the window logs were added the same day.
# The user also stages, amends and pushes from VS Code's Source Control panel, which neither shows, so --vscode reads the Git log VS Code keeps of the commands it runs for the user.
# Both keep everything, so a view such as today or since Windows started is chosen when reading; the record's first 500 commands, seeded from the old ~/.bash_history, have no times and are skipped. (Claude code Opus 5.5) -->

# <!-- custom: argparse parses the options, datetime turns the record's Unix times and the prompts' times into local times, pathlib finds the record and logs, re reads the --since forms and strips terminal codes, subprocess asks Windows for its boot time, sys reports errors. (Claude code Opus 5.5) -->
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import re
import subprocess
import sys

# <!-- custom: pyte, a terminal emulator in pure Python (pip install pyte), replays a window log as the window showed it; only --output needs it. (Claude code Opus 5.5) -->
try:
	import pyte
except ImportError:
	pyte = None

FOLDER = Path.home() / "Downloads" / "AdvCiv-SAS_LLM" / "git_bash_history"
RECORD = FOLDER / "bash_history.txt"
TIME_LINE = re.compile(r"^#(\d{9,11})$")
PROMPT_TIME = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)$")
LOG_NAME = re.compile(r"^window_(\d{8}_\d{6})\.log$")
# <!-- custom: VS Code writes one Git.log per window and session under %APPDATA%\Code\logs, keeping about the last 10 sessions; most lines are its own polling, such as status, for-each-ref or show, so only commands that change something for the user are kept: a commit or amend (run as git -c user.useConfigOnly=true commit), push, staging (add) and unstaging (reset), and the like. (Claude code Opus 5.5) -->
VSCODE_LOGS = Path.home() / "AppData" / "Roaming" / "Code" / "logs"
VSCODE_LINE = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\.\d+ \[info\] > (git (?:-c \S+ )*(?:commit|push|pull|add|reset|restore|checkout|switch|merge|rebase|cherry-pick|revert|stash|tag|rm|mv)(?= |$).*?)(?: \[\d+ms\])?$")


def entries(text):
	# <!-- custom: Bash writes "#<Unix time>" before each command when HISTTIMEFORMAT is set; commands without one, such as the seeded ones, get None. (Claude code Opus 5.5) -->
	result, when = [], None
	for line in text.splitlines():
		match = TIME_LINE.match(line)
		if match:
			when = datetime.fromtimestamp(int(match.group(1)))
			continue
		if line.strip():
			result.append((when, line))
		when = None
	return result


def screen_rows(screen, rows):
	return ["".join(row[x].data for x in range(screen.columns)) for row in rows]


def clean_log(raw, columns):
	# <!-- custom: A window log is the raw stream sent to the window, not the text it shows: the first reader only stripped its control codes, and on 2026-11-17 a prompt merged with the command typed after it and long git log lines lost text in the middle, as readline redraws a line and Git erases and rewrites its progress lines with cursor moves.
	# So the stream is replayed on a pyte screen as wide as the window, which applies those moves as the window does; columns must match the window's, or rows wrap elsewhere. (Claude code Opus 5.5) -->
	if pyte is None:
		sys.exit("--output needs pyte, a terminal emulator in pure Python: python -m pip install pyte")
	lines, screen = [], pyte.HistoryScreen(columns, 48, history=1000000)
	# <!-- custom: Bash's prompt holds a bare line feed, which mintty shows as a new line from column 0; pyte only moves down unless in new-line mode (LNM), which left the first test's prompts merged with the line above. (Claude code Opus 5.5) -->
	screen.set_mode(pyte.modes.LNM)
	# <!-- custom: clear wipes the screen (ESC [ 2 J, then ESC [ 3 J for the scrollback), so its rows are kept first, or a cleared push would vanish from the transcript. (Claude code Opus 5.5) -->
	plain_erase = screen.erase_in_display

	def erase_in_display(how=0, *args, **kwargs):
		if how in (2, 3):
			lines.extend(screen_rows(screen, screen.history.top))
			screen.history.top.clear()
			if how == 2:
				lines.extend(screen_rows(screen, (screen.buffer[y] for y in range(screen.lines))))
		plain_erase(how, *args, **kwargs)
	screen.erase_in_display = erase_in_display
	pyte.Stream(screen).feed(raw)
	lines.extend(screen_rows(screen, screen.history.top))
	lines.extend(screen_rows(screen, (screen.buffer[y] for y in range(screen.lines))))
	# <!-- custom: A row filled to the last column continued on the next one, so the two are joined again, as mintty does when the user copies the window's text. (Claude code Opus 5.5) -->
	joined = []
	for row in lines:
		if joined and len(joined[-1]) % columns == 0 and joined[-1][-1:] != " ":
			joined[-1] += row
		else:
			joined.append(row)
	return [row.rstrip() for row in joined]


def window_blocks(path, columns):
	# <!-- custom: ~/.bashrc puts the time on its own line before each prompt, so each block runs from one time to the next: the prompt, the command typed there, and its output. (Claude code Opus 5.5) -->
	blocks, when, current = [], None, []
	for line in clean_log(path.read_bytes().decode("utf-8", errors="replace"), columns):
		match = PROMPT_TIME.match(line)
		if match:
			if current:
				blocks.append((when, current))
			when, current = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S"), [line]
		elif line or current:
			current.append(line)
	if current:
		blocks.append((when, current))
	return blocks


def boot_time():
	command = "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToString('yyyy-MM-ddTHH:mm:ss')"
	output = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True, text=True, check=True).stdout.strip()
	return datetime.fromisoformat(output)


def parse_since(value, now):
	if value == "today":
		return now.replace(hour=0, minute=0, second=0, microsecond=0)
	if value == "boot":
		return boot_time()
	hours = re.fullmatch(r"(\d+)h", value)
	if hours:
		return now - timedelta(hours=int(hours.group(1)))
	# <!-- custom: Minutes too, as checking one recent amend with --since 30m failed on 2026-11-17 when only hours were read. (Claude code Opus 5.5) -->
	minutes = re.fullmatch(r"(\d+)m", value)
	if minutes:
		return now - timedelta(minutes=int(minutes.group(1)))
	return datetime.fromisoformat(value)


def print_commands(record, since):
	if not record.is_file():
		sys.exit("no command record at %s; see the Git Bash section of README_Desktop_Windows.md" % record)
	timed = [(when, command) for when, command in entries(record.read_text(encoding="utf-8", errors="replace")) if when is not None]
	shown = [(when, command) for when, command in timed if when >= since]
	for when, command in shown:
		print("%s  %s" % (when.strftime("%Y-%m-%d %H:%M:%S"), command))
	# <!-- custom: A window opened before the record was set up still saves the old way, on closing, so an empty result can mean that rather than no commands.
	# The count goes to standard error after the list is flushed: piped together, the buffered list otherwise came after it, as in the first sample in the docs. (Claude code Opus 5.5) -->
	sys.stdout.flush()
	print("%d command(s) since %s, of %d timed in the record" % (len(shown), since.strftime("%Y-%m-%d %H:%M:%S"), len(timed)), file=sys.stderr)


def print_output(folder, since, columns):
	logs = sorted(path for path in folder.glob("window_*.log") if LOG_NAME.match(path.name))
	shown = 0
	for path in logs:
		# <!-- custom: A log's name is the time its window opened, so a window still open from before --since can hold later blocks: it is read whenever it was written to since. (Claude code Opus 5.5) -->
		if datetime.fromtimestamp(path.stat().st_mtime) < since:
			continue
		blocks = [(when, lines) for when, lines in window_blocks(path, columns) if when is not None and when >= since]
		if not blocks:
			continue
		print("=== %s" % path.name)
		for when, lines in blocks:
			print("\n".join(lines).rstrip())
			shown += 1
	sys.stdout.flush()
	print("%d prompt(s) since %s, from %d window log(s)" % (shown, since.strftime("%Y-%m-%d %H:%M:%S"), len(logs)), file=sys.stderr)


def print_vscode(folder, since):
	actions = set()
	for path in folder.glob("*/window*/exthost/vscode.git/Git.log"):
		if datetime.fromtimestamp(path.stat().st_mtime) < since:
			continue
		for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
			match = VSCODE_LINE.match(line)
			if match:
				when = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
				if when >= since:
					actions.add((when, match.group(2)))
	for when, command in sorted(actions):
		print("%s  %s" % (when.strftime("%Y-%m-%d %H:%M:%S"), command))
	sys.stdout.flush()
	print("%d VS Code Git action(s) since %s" % (len(actions), since.strftime("%Y-%m-%d %H:%M:%S")), file=sys.stderr)


def main():
	parser = argparse.ArgumentParser(description="Print what the user did in Git since a given time: the Git Bash commands from the record ~/.bashrc writes, with --output the Git Bash windows' full text from the logs ~/.minttyrc writes, or with --vscode the Git actions taken in VS Code.")
	parser.add_argument("--since", default="today", help="today (default), boot (since Windows started), a number of hours or minutes such as 2h or 30m, or a time such as 2026-11-17T13:00")
	parser.add_argument("--output", action="store_true", help="print the windows' full text, Git's answers included, instead of the commands alone")
	parser.add_argument("--vscode", action="store_true", help="print the Git actions the user took in VS Code's Source Control panel, such as staging, amending or pushing, from VS Code's own Git log")
	parser.add_argument("--record", type=Path, default=RECORD)
	parser.add_argument("--folder", type=Path, default=FOLDER, help="where the window logs are")
	parser.add_argument("--columns", type=int, default=160, help="the window's width in characters, Columns in ~/.minttyrc; --output wraps rows at it")
	args = parser.parse_args()
	since = parse_since(args.since, datetime.now())
	if args.vscode:
		print_vscode(VSCODE_LOGS, since)
	elif args.output:
		print_output(args.folder, since, args.columns)
	else:
		print_commands(args.record, since)
	return 0


if __name__ == "__main__":
	sys.exit(main())

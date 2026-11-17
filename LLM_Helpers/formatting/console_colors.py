#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Shared console colors for our helpers, by role rather than by color, so every tool that prints for a person reads alike: first written in SASPilotConsole.py, then moved here at the user's request so other helpers reuse them (2026-11-14).
# The roles and colors are the ones the user chose for SASPilotConsole: errors red, banners yellow, results sky blue, notes bold orchid, code light green; plain text keeps the console's own color. (Claude code Opus 5.5) -->

# <!-- custom: html escapes text for to_html, re finds the color codes, sys checks whether output is a console. (Claude code Opus 5.5) -->
import html
import re
import sys

# <!-- custom: 256-color codes (38;5;n) for sky blue and light green: a fresh Windows 10 console showed all five roles once virtual-terminal processing was on (2026-11-14).
# HTML gives each role's color for to_html. (Claude code Opus 5.5) -->
ROLES = {
	"error": ("\x1b[91m", "#ff5555"),
	"banner": ("\x1b[93m", "#ffff55"),
	"result": ("\x1b[38;5;117m", "#87d7ff"),
	# <!-- custom: The agent's notes, its reasons, were bright white at first and hardly stood out from the plain text; the user found them the most useful lines for a watcher and asked for a color (2026-11-14), so bold orchid (256-color 213), unlike the other roles. (Claude code Opus 5.5) -->
	"note": ("\x1b[1;38;5;213m", "#ff87ff"),
	"code": ("\x1b[38;5;120m", "#87ff87"),
}
RESET = "\x1b[0m"
# <!-- custom: The console's own text color, which plain text keeps, and its background, for to_html. (Claude code Opus 5.5) -->
PLAIN_HTML = "#cccccc"
BACKGROUND_HTML = "#0c0c0c"

_state = {"on": False}


def enable(stream=None):
	# <!-- custom: A Windows console shows ANSI codes as text until virtual-terminal processing (ENABLE_VIRTUAL_TERMINAL_PROCESSING, 4) is set on its output handle.
	# Off when that fails or the output is not a console, such as a pipe or a file, so piped output stays plain.
	# Returns whether colors are on. (Claude code Opus 5.5) -->
	stream = stream or sys.stdout
	_state["on"] = False
	if not stream.isatty():
		return False
	if sys.platform == "win32":
		# <!-- custom: ctypes switches the Windows console to read colour codes; imported only on Windows. (Claude code Opus 5.5) -->
		import ctypes
		kernel32 = ctypes.windll.kernel32
		handle = kernel32.GetStdHandle(-11)
		mode = ctypes.c_ulong()
		if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
			return False
		if not kernel32.SetConsoleMode(handle, mode.value | 4):
			return False
	_state["on"] = True
	return True


def set_enabled(on):
	# <!-- custom: For callers that render to a file rather than a console, such as to_html, which needs the codes whatever the console. (Claude code Opus 5.5) -->
	_state["on"] = bool(on)


def is_enabled():
	return _state["on"]


def paint(text, role):
	if not _state["on"]:
		return text
	return ROLES[role][0] + text + RESET


def to_html(text, title="console"):
	# <!-- custom: Colored console text as a standalone HTML page in the same colors, for documentation: a page shows what the console showed, where a screenshot cannot be searched or copied.
	# Only the codes in ROLES are known; any other code is dropped. (Claude code Opus 5.5) -->
	colors = {}
	for (code, color) in ROLES.values():
		colors[code] = color
	parts = []
	current = None
	position = 0
	for match in re.finditer("\x1b\\[[0-9;]*m", text):
		parts.append((current, text[position:match.start()]))
		code = match.group(0)
		if code == RESET:
			current = None
		else:
			current = colors.get(code)
		position = match.end()
	parts.append((current, text[position:]))
	body = []
	for (color, chunk) in parts:
		if not chunk:
			continue
		escaped = html.escape(chunk)
		if color:
			body.append('<span style="color:%s">%s</span>' % (color, escaped))
		else:
			body.append(escaped)
	return '<!doctype html>\n<html><head><meta charset="utf-8"><title>%s</title></head>\n<body style="background:%s;color:%s;margin:0;padding:12px">\n<pre style="font-family:Consolas,monospace;font-size:13px;white-space:pre-wrap">%s</pre>\n</body></html>\n' % (html.escape(title), BACKGROUND_HTML, PLAIN_HTML, "".join(body))

# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Windows-side helpers for a running Civ4 window or any other app's: find it by process ID, take a screenshot, click, hover, scroll, paste text, press a key, close it, or launch Civ4 detached from the caller.
# Named civ4_window.py until 2026-11-10, before its first commit; renamed once it also drove other agents' apps such as Codex and the Claude app.
# Coordinates are physical pixels relative to the window's top-left corner, as in the screenshots; the process is made DPI-aware first, because without it a 150% display scale returned a 1284x747 rectangle for a 1926x1120 window and cropped the screenshot.
# Mouse clicks reached the game before key events did.
# After key events gained scan codes on 2026-11-11, agents navigated Sevopedia and started and stopped autoplay with Ctrl+Shift+X. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->

# <!-- custom: argparse parses the subcommands; ctypes calls user32/gdi32/kernel32 for windows, input and bitmaps. (Claude Code Opus 5.5) -->
import argparse
import ctypes
import ctypes.wintypes as wt
# <!-- custom: json reads and writes the named window layouts of 'positions'. (Claude Code Opus 5.5) -->
from importlib import import_module
import json
# <!-- custom: subprocess runs PowerShell for WMI; sys, time and pathlib handle exit codes, waits and paths. (Claude Code Opus 5.5) -->
# <!-- custom: os finds the crash dump's folder, shutil copies it and struct reads the process ID it records, for 'dump'. See KI#1089. (Claude code Opus 5.5) -->
import os
import shutil
import struct
# <!-- custom: re reads a client's mod from its command line or ini= file. (Claude Code Opus 5.5) -->
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
format_json = import_module("formatting.json_format").format_json

USER32 = ctypes.windll.user32
WM_CLOSE = 0x0010
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

# <!-- custom: Civ4 lives here on the development machine; pass --civ4-dir elsewhere. (Claude Code Opus 5.5) -->
DEFAULT_CIV4_DIR = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword")
EXE_NAME = "Civ4BeyondSword.exe"


def make_dpi_aware():
	try:
		ctypes.windll.shcore.SetProcessDpiAwareness(2)
	except (AttributeError, OSError):
		USER32.SetProcessDPIAware()


def find_window(pid):
	# <!-- custom: Return the visible top-level window owned by pid that has a title, or None. (Claude Code Opus 5.5) -->
	found = []
	proc_type = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

	def callback(hwnd, _lparam):
		owner = wt.DWORD()
		USER32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
		if owner.value == pid and USER32.IsWindowVisible(hwnd) and USER32.GetWindowTextLengthW(hwnd) > 0:
			found.append(hwnd)
		return True

	USER32.EnumWindows(proc_type(callback), 0)
	return found[0] if found else None


def window_rect(hwnd):
	# <!-- custom: Made DPI-aware here too, as screenshot and window_point already were: helpers that imported this module and called window_rect directly read, at 150% scaling, a 1926 x 1120 Civ4 window as 1284 x 747 (map_preview_dds.py's size check, 2026-11-12). (Claude code Opus 5.5) -->
	make_dpi_aware()
	rect = wt.RECT()
	if not USER32.GetWindowRect(hwnd, ctypes.byref(rect)):
		raise OSError("GetWindowRect failed")
	return rect.left, rect.top, rect.right, rect.bottom


def window_title(hwnd):
	buffer = ctypes.create_unicode_buffer(256)
	USER32.GetWindowTextW(hwnd, buffer, 256)
	return buffer.value


def print_window_image(hwnd):
	# <!-- custom: Ask the window to draw itself into a bitmap (PrintWindow with PW_RENDERFULLCONTENT), so it need not be in front or uncovered.
	# Tested 2026-11-10 during autoplay: with Notepad covering the game it still captured the game, two captures 3 seconds apart differed as turns advanced, and a minimized window gave only its 237x39 title bar. (Claude Code Opus 5.5) -->
	# <!-- custom: Pillow turns the PrintWindow bitmap into an image; imported here so list/click/close work without it. (Claude Code Opus 5.5) -->
	from PIL import Image
	gdi32 = ctypes.windll.gdi32
	left, top, right, bottom = window_rect(hwnd)
	width, height = right - left, bottom - top
	window_dc = USER32.GetWindowDC(hwnd)
	memory_dc = gdi32.CreateCompatibleDC(window_dc)
	bitmap = gdi32.CreateCompatibleBitmap(window_dc, width, height)
	old = gdi32.SelectObject(memory_dc, bitmap)
	try:
		if not USER32.PrintWindow(hwnd, memory_dc, 2):
			raise OSError("PrintWindow failed")

		class BITMAPINFOHEADER(ctypes.Structure):
			_fields_ = [("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG), ("biPlanes", wt.WORD), ("biBitCount", wt.WORD), ("biCompression", wt.DWORD), ("biSizeImage", wt.DWORD), ("biXPelsPerMeter", wt.LONG), ("biYPelsPerMeter", wt.LONG), ("biClrUsed", wt.DWORD), ("biClrImportant", wt.DWORD)]

		header = BITMAPINFOHEADER(ctypes.sizeof(BITMAPINFOHEADER), width, -height, 1, 32, 0, 0, 0, 0, 0, 0)
		buffer = ctypes.create_string_buffer(width * height * 4)
		if not gdi32.GetDIBits(memory_dc, bitmap, 0, height, buffer, ctypes.byref(header), 0):
			raise OSError("GetDIBits failed")
		return Image.frombuffer("RGB", (width, height), buffer, "raw", "BGRX", 0, 1)
	finally:
		gdi32.SelectObject(memory_dc, old)
		gdi32.DeleteObject(bitmap)
		gdi32.DeleteDC(memory_dc)
		USER32.ReleaseDC(hwnd, window_dc)


def browser_page_box(hwnd):
	# <!-- custom: The web page's rectangle in a Chromium browser window, in window pixels, from the browser's own UI Automation tree: the MultiContentsView panel that holds the tabs' contents.
	# The tab strip, address bar and bookmarks bar above it vary with the window size, display scale and which bars are shown (182 screen pixels on the user's maximized 4K Chrome, 2026-11-17), so reading the panel replaces a fixed crop.
	# Cropping them keeps the user's other tabs, address and bookmarks out of the agent's chat and any shared screenshot, since the task needs only the page. (Claude code Opus 5.5) -->
	command = "Add-Type -AssemblyName UIAutomationClient; $w = [System.Windows.Automation.AutomationElement]::FromHandle([IntPtr]%d); foreach ($e in $w.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)) { if ($e.Current.ClassName -eq 'MultiContentsView') { $r = $e.Current.BoundingRectangle; \"$($r.Left) $($r.Top) $($r.Right) $($r.Bottom)\"; break } }" % hwnd
	output = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True, text=True, check=True).stdout.split()
	if len(output) != 4:
		raise RuntimeError("no browser page panel in this window; --page reads Chrome's window")
	left, top = window_rect(hwnd)[:2]
	page = [int(float(value)) for value in output]
	return page[0] - left, page[1] - top, page[2] - left, page[3] - top


def screenshot(pid, out_path, method="window", crop=None, scale=1.0, page=False):
	# <!-- custom: Added page, which replaces crop with the web page's rectangle from browser_page_box, so the --page option can crop Chrome to its page without a measured crop. (Claude code Opus 5.5) -->
	# <!-- custom: method "window": PrintWindow, which leaves the window where it is; "screen": bring the window to the front and grab its screen area. (Claude Code Opus 5.5) -->
	# <!-- custom: Pillow's ImageGrab copies the window's screen area for the screen method. (Claude Code Opus 5.5) -->
	from PIL import ImageGrab
	make_dpi_aware()
	hwnd = find_window(pid)
	if hwnd is None:
		raise RuntimeError("no visible window for process %d" % pid)
	box = window_rect(hwnd)
	if method == "window":
		image = print_window_image(hwnd)
	elif method == "screen":
		USER32.SetForegroundWindow(hwnd)
		time.sleep(0.4)
		box = window_rect(hwnd)
		image = ImageGrab.grab(bbox=box, all_screens=True)
	else:
		raise ValueError("unknown screenshot method %r" % method)
	if page:
		crop = browser_page_box(hwnd)
	# <!-- custom: crop is (left, top, right, bottom) in window pixels and scale shrinks the result: a full 3840-pixel window cost many tokens per read, so on 2026-11-10 nearly every screenshot was cropped and shrunk with throwaway Pillow code; these two options replace it. (Claude Code Opus 5.5) -->
	if crop:
		image = image.crop(tuple(crop))
	if scale != 1.0:
		image = image.resize((max(1, int(image.width * scale)), max(1, int(image.height * scale))))
	out_path = Path(out_path)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	# <!-- custom: Captures are kept as PNG on purpose, though heavier: a 1926 x 1120 Civ4 window took 2.9 MB, against 262 KB for Civ4's own Print Screen JPG (2026-11-22).
	# A PNG can be converted to JPG later for sharing, but a JPG cannot get back what it lost (the user). (Claude code Opus 5.5) -->
	image.save(out_path)
	return out_path, box


def save_clipboard_image(out_path, crop=None, scale=1.0):
	# <!-- custom: Save an image the user copied, such as a full-screen capture of a moment an agent cannot catch itself (a queued message, a tooltip), as on 2026-11-10.
	# crop is in screen pixels of the capture. (Claude Code Opus 5.5) -->
	# <!-- custom: Pillow's ImageGrab reads the clipboard image. (Claude Code Opus 5.5) -->
	from PIL import ImageGrab
	image = ImageGrab.grabclipboard()
	if image is None or isinstance(image, list):
		raise RuntimeError("the clipboard holds no image")
	if crop:
		image = image.crop(tuple(crop))
	if scale != 1.0:
		image = image.resize((max(1, int(image.width * scale)), max(1, int(image.height * scale))))
	out_path = Path(out_path)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	image.save(out_path)
	return out_path, image.size


def window_point(pid, x, y):
	# <!-- custom: Shared by click, hover and scroll: find pid's window and turn a window-relative point into a screen point, refusing one outside the window. (Claude Code Opus 5.5) -->
	make_dpi_aware()
	hwnd = find_window(pid)
	if hwnd is None:
		raise RuntimeError("no visible window for process %d" % pid)
	left, top, right, bottom = window_rect(hwnd)
	if not (0 <= x < right - left and 0 <= y < bottom - top):
		raise ValueError("point %d,%d lies outside the %dx%d window" % (x, y, right - left, bottom - top))
	return hwnd, left + x, top + y


def client_offset(pid):
	# <!-- custom: Where the game area starts inside pid's window, as a window-relative point: Civ4's own screenshots and its 1920 x 1080 layouts count from there, while click, hover and screenshot count from the window's corner, title bar and border included (3, 37 for a windowed 1920 x 1080 client on 2026-11-21). (Claude Code Opus 5.5) -->
	make_dpi_aware()
	hwnd = find_window(pid)
	if hwnd is None:
		raise RuntimeError("no visible window for process %d" % pid)
	left, top, _right, _bottom = window_rect(hwnd)
	origin = wt.POINT(0, 0)
	# <!-- custom: ClientToScreen's result is checked, as a failure left the point at 0, 0 and gave a wrong offset rather than an error (Codex's review of the main port). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if not USER32.ClientToScreen(hwnd, ctypes.byref(origin)):
		raise RuntimeError("ClientToScreen failed for process %d's window" % pid)
	return origin.x - left, origin.y - top


def window_pid(hwnd):
	owner = wt.DWORD()
	USER32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
	return owner.value


def process_elevated(pid):
	# <!-- custom: True when the process runs with administrator rights, read from its token; a token this tool may not open counts as elevated, as only a higher-rights process refuses.
	# Lets click name the real cause when Windows blocks its input. (Claude code Opus 5.5) -->
	kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
	advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
	kernel32.OpenProcess.restype = wt.HANDLE
	process = kernel32.OpenProcess(0x1000, False, pid)
	if not process:
		return False
	token = wt.HANDLE()
	try:
		if not advapi32.OpenProcessToken(process, 0x0008, ctypes.byref(token)):
			return ctypes.get_last_error() == 5
		elevation = wt.DWORD()
		size = wt.DWORD()
		advapi32.GetTokenInformation(token, 20, ctypes.byref(elevation), ctypes.sizeof(elevation), ctypes.byref(size))
		return bool(elevation.value)
	finally:
		if token:
			kernel32.CloseHandle(token)
		kernel32.CloseHandle(process)


def bring_to_front(hwnd, pid, allow_click=True):
	# <!-- custom: Focus restoration passes allow_click=False so returning to the user's window never presses its title bar. (GPT-6.1-Sol) -->
	# <!-- custom: Windows' foreground lock refuses SetForegroundWindow from a background process: on 2026-11-10 pastes between the Codex and Claude apps failed twice, each time leaving the app last typed into in front.
	# Retrying with this thread attached to the foreground window's input thread, the usual workaround, lets the switch through; the click and paste checks still refuse if it does not. (Claude Code Opus 5.5) -->
	USER32.SetForegroundWindow(hwnd)
	time.sleep(0.15)
	foreground = USER32.GetForegroundWindow()
	if window_pid(foreground) == pid:
		return foreground
	kernel32 = ctypes.windll.kernel32
	foreground_thread = USER32.GetWindowThreadProcessId(foreground, None)
	our_thread = kernel32.GetCurrentThreadId()
	USER32.AttachThreadInput(our_thread, foreground_thread, True)
	try:
		USER32.BringWindowToTop(hwnd)
		USER32.SetForegroundWindow(hwnd)
	finally:
		USER32.AttachThreadInput(our_thread, foreground_thread, False)
	time.sleep(0.3)
	foreground = USER32.GetForegroundWindow()
	if window_pid(foreground) == pid:
		return foreground
	# <!-- custom: On 2026-11-11 both attempts failed for Civ4 five times running while the user was idle, yet a real click on its title bar brought it forward at once; a click is user input, which the foreground lock lets through.
	# The title bar is clicked because it does nothing inside a game. (Claude Code Opus 5.5) -->
	# <!-- custom: Codex's 2026-11-11 review found the click could land in another app covering that point; so check the window under it first, and never click while giving focus back to the user's window. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
	left, top, right, _bottom = window_rect(hwnd)
	title_x, title_y = left + (right - left) // 3, top + 12
	under = USER32.WindowFromPoint(wt.POINT(title_x, title_y))
	if not allow_click or not under or window_pid(under) != pid:
		return foreground
	USER32.SetCursorPos(title_x, title_y)
	time.sleep(0.05)
	USER32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
	USER32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
	time.sleep(0.4)
	return USER32.GetForegroundWindow()


def click(pid, x, y, modifiers=(), double=False, give_back=False, button="left"):
	# <!-- custom: button picks the mouse button from DRAG_BUTTONS; a right click opens the Sevopedia from many Civ4 widgets, which agents could not test before (2026-11-20). (Claude code Opus 5.5) -->
	_, button_down_flag, button_up_flag = DRAG_BUTTONS[button]
	# <!-- custom: give_back returns the focus to the user's window after the click.
	# Only the command line sets it: paste calls click first, and giving the focus back there made Ctrl+V land in the user's window on 2026-11-17. (Claude code Opus 5.5) -->
	# <!-- custom: The caller can request a chord or double click so both forms use the same bounds and ownership checks. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
	# <!-- custom: Codex's 2026-11-10 review found that click pressed the mouse even when the window had not come to the front or the point lay outside it, so the click could land in whatever window was there, such as the user's.
	# Check the bounds, the foreground window and the window under the point before pressing; a Civ4 popup is a separate window of the same process, so the last check compares processes, not handles. (Claude Code Opus 5.5) -->
	hwnd, screen_x, screen_y = window_point(pid, x, y)
	previous = USER32.GetForegroundWindow()
	foreground = bring_to_front(hwnd, pid)
	if window_pid(foreground) != pid:
		raise RuntimeError("process %d's window did not come to the front; the foreground window belongs to process %d" % (pid, window_pid(foreground)))
	under = USER32.WindowFromPoint(wt.POINT(screen_x, screen_y))
	if not under or window_pid(under) != pid:
		raise RuntimeError("screen point %d,%d is covered by a window of process %d" % (screen_x, screen_y, window_pid(under) if under else 0))
	USER32.SetCursorPos(screen_x, screen_y)
	time.sleep(0.05)
	# <!-- custom: The idle wait and the checks above all come before the cursor moves, so a user moving the mouse or switching windows in the last instant would send the press somewhere else; check both once more just before pressing.
	# The user asked for this on 2026-11-17, while working in other windows during an agent's clicks. (Claude code Opus 5.5) -->
	cursor = wt.POINT()
	USER32.GetCursorPos(ctypes.byref(cursor))
	if (cursor.x, cursor.y) != (screen_x, screen_y):
		# <!-- custom: Windows refuses to move the cursor or send input into an elevated window from a program that is not, so this check tripped each time on the user's Task Manager on 2026-11-26 and blamed a mouse move; it now says why. (Claude code Opus 5.5) -->
		if process_elevated(pid) and not process_elevated(os.getpid()):
			raise RuntimeError("process %d runs elevated, and Windows keeps input from this non-elevated tool out of its windows; nothing was pressed" % pid)
		raise RuntimeError("the mouse moved to %d,%d before the click at %d,%d; nothing was pressed" % (cursor.x, cursor.y, screen_x, screen_y))
	if window_pid(USER32.GetForegroundWindow()) != pid:
		raise RuntimeError("another window came to the front before the click; nothing was pressed")
	# <!-- custom: Civ4 gives Ctrl-, Shift- and Alt-clicks their own meanings, such as selecting all units of a type or queueing production, so modifiers are held around the click. (Claude Code Opus 5.5) -->
	# <!-- custom: Presses sit inside the try and only what was pressed is released, so a Ctrl+C mid-click leaves no key or button held, as Codex's 2026-11-11 review reproduced. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
	pressed, button_down = [], False
	try:
		for modifier in modifiers:
			key_event(modifier)
			pressed.append(modifier)
			time.sleep(0.04)
		# <!-- custom: double presses twice within the double-click time, as opening a city from its banner needs. (Claude Code Opus 5.5) -->
		for _ in range(2 if double else 1):
			USER32.mouse_event(button_down_flag, 0, 0, 0, 0)
			button_down = True
			time.sleep(0.05)
			USER32.mouse_event(button_up_flag, 0, 0, 0, 0)
			button_down = False
			time.sleep(0.05)
	finally:
		if button_down:
			USER32.mouse_event(button_up_flag, 0, 0, 0, 0)
		for modifier in reversed(pressed):
			key_event(modifier, up=True)
	# <!-- custom: key, type and paste gave the focus back to the user's window, but click left the target in front, so a user working in VS Code during an agent's clicks found Civ4 in front (2026-11-17).
	# Only the click command does it, through give_back: paste calls click to focus a message box before pressing Ctrl+V, and when click gave the focus back first, three pastes meant for Codex went to the user's window instead, the same day.
	# Scripts chaining clicks, such as set_dropdown.py opening a dropdown and then picking an option, keep the focus between them too. (Claude code Opus 5.5) -->
	if give_back:
		# <!-- custom: Hold a moment so the game reads the click on its own frames, as key does, before giving the focus back. (Claude code Opus 5.5) -->
		time.sleep(0.3)
		give_focus_back(previous, pid)
	return screen_x, screen_y


DRAG_BUTTONS = {"left": (0x01, MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP), "right": (0x02, 0x0008, 0x0010), "middle": (0x04, 0x0020, 0x0040)}


def drag(pid, x1, y1, x2, y2, button="left", steps=20, modifiers=()):
	# <!-- custom: Press a mouse button at one window point, move in steps to another and release, to turn or move a 3D view such as the Sevopedia's model panes.
	# Both ends get click's checks, and only what was pressed is released. (Claude Code Opus 5.5) -->
	if steps < 1:
		raise ValueError("drag steps must be positive")
	vk, down, up = DRAG_BUTTONS[button]
	# <!-- custom: An idle interval can pass while a button or modifier is held.
	# Refuse that drag so cleanup cannot release the user's input. (GPT-6.1-Sol) -->
	if any(USER32.GetAsyncKeyState(key) & 0x8000 for key in (vk, *modifiers)):
		raise RuntimeError("a requested drag button or modifier is already held")
	hwnd, _, _ = window_point(pid, x1, y1)
	window_point(pid, x2, y2)
	foreground = bring_to_front(hwnd, pid)
	if window_pid(foreground) != pid:
		raise RuntimeError("process %d's window did not come to the front; the foreground window belongs to process %d" % (pid, window_pid(foreground)))
	_, start_x, start_y = window_point(pid, x1, y1)
	_, end_x, end_y = window_point(pid, x2, y2)
	for screen_x, screen_y in ((start_x, start_y), (end_x, end_y)):
		under = USER32.WindowFromPoint(wt.POINT(screen_x, screen_y))
		if not under or window_pid(under) != pid:
			raise RuntimeError("screen point %d,%d is covered by a window of process %d" % (screen_x, screen_y, window_pid(under) if under else 0))
	if not USER32.SetCursorPos(start_x, start_y):
		raise OSError("could not position pointer for drag")
	time.sleep(0.05)
	pressed, button_down = [], False
	try:
		for modifier in modifiers:
			key_event(modifier)
			pressed.append(modifier)
			time.sleep(0.04)
		# <!-- custom: Focus can change during a drag.
		# Stop moving and let finally release the button and modifiers if that happens. (GPT-6.1-Sol) -->
		under = USER32.WindowFromPoint(wt.POINT(start_x, start_y))
		if window_pid(USER32.GetForegroundWindow()) != pid or not under or window_pid(under) != pid:
			raise RuntimeError("drag target changed before pressing the button")
		USER32.mouse_event(down, 0, 0, 0, 0)
		button_down = True
		time.sleep(0.1)
		for step in range(1, steps + 1):
			if window_pid(USER32.GetForegroundWindow()) != pid:
				raise RuntimeError("drag target lost focus")
			x = start_x + (end_x - start_x) * step // steps
			y = start_y + (end_y - start_y) * step // steps
			if not USER32.SetCursorPos(x, y):
				raise OSError("could not move pointer during drag")
			time.sleep(0.03)
		time.sleep(0.1)
	finally:
		if button_down:
			USER32.mouse_event(up, 0, 0, 0, 0)
		for modifier in reversed(pressed):
			key_event(modifier, up=True)
	return (start_x, start_y), (end_x, end_y)


def hover(pid, x, y, front=False):
	# <!-- custom: Move the pointer without clicking or focusing, to reveal tooltips such as Codex's usage reset times.
	# A click into the Claude app while the user typed there would have taken focus from their typing; a hover takes none. (Claude Code Opus 5.5) -->
	# <!-- custom: Civ4's plot help ignored a pointer only placed with SetCursorPos: on 2026-11-22, checking KI#11.3, it kept an earlier plot's help, and only the user's own click woke it.
	# Writing "click Civ4 first" in the Game Runs guide had not helped, so the tool now does it: front=True brings the window forward through its title bar, which does nothing in a game, then a 1-pixel real mouse move there and back makes the game read the new point; tested on plot (40,17), whose help then appeared. (Claude Code Opus 5.5) -->
	hwnd, screen_x, screen_y = window_point(pid, x, y)
	if front:
		bring_to_front(hwnd, pid, allow_click=True)
		time.sleep(0.3)
	USER32.SetCursorPos(screen_x, screen_y)
	for step in (1, -1):
		USER32.mouse_event(MOUSEEVENTF_MOVE, step, 0, 0, 0)
		time.sleep(0.05)
	return screen_x, screen_y


def scroll(pid, x, y, clicks):
	# <!-- custom: Wheel events reach the window under the pointer without focusing it (Windows 10 scrolls inactive windows), so scrolling, like hovering, leaves the user's typing alone.
	# Positive clicks scroll up, negative down; one click is one wheel notch (120). (Claude Code Opus 5.5) -->
	hover(pid, x, y)
	step = 120 if clicks > 0 else -120
	for _ in range(abs(clicks)):
		USER32.mouse_event(0x0800, 0, 0, ctypes.c_uint32(step).value, 0)
		time.sleep(0.03)


CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002
KEYEVENTF_KEYUP = 0x0002
VK_CONTROL = 0x11
# <!-- custom: Each key is (virtual key, modifiers); ctrl+enter queues a message in the Claude app or Codex while it works ("Ctrl+Enter to queue for later"); ctrl+a then backspace clears a box the agent filled itself. (Claude Code Opus 5.5) -->
KEYS = {"enter": (0x0D, ()), "esc": (0x1B, ()), "ctrl+enter": (0x0D, (VK_CONTROL,)), "ctrl+a": (ord("A"), (VK_CONTROL,)), "backspace": (0x08, ()),
	"left": (0x25, ()), "up": (0x26, ()), "right": (0x27, ()), "down": (0x28, ()), "pgup": (0x21, ()), "pgdn": (0x22, ()), "home": (0x24, ()), "end": (0x23, ()),
	# <!-- custom: Print Screen makes Civ4 save its own screenshot of the game area, in the format the INI names (JPG by default), to ScreenShots (2026-11-21, for the docs' screenshots). (Claude Code Opus 5.5) -->
	"printscreen": (0x2C, ())}
KEYEVENTF_EXTENDEDKEY = 0x0001
# <!-- custom: Arrow, page, home, end, insert and delete keys sit on the extended keyboard, so their events need KEYEVENTF_EXTENDEDKEY, or a program reading scan codes sees the number pad's keys instead. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
EXTENDED_KEYS = {0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x2C, 0x2D, 0x2E}


def clipboard_text():
	# <!-- custom: Return the clipboard's text, or None when it holds none, so paste can put the user's clipboard back.
	# Pointer-sized results need explicit restypes on 64-bit Python, or ctypes truncates them to int. (Claude Code Opus 5.5) -->
	kernel32 = ctypes.windll.kernel32
	USER32.GetClipboardData.restype = ctypes.c_void_p
	kernel32.GlobalLock.restype = ctypes.c_void_p
	kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
	kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
	if not USER32.OpenClipboard(None):
		raise OSError("OpenClipboard failed")
	try:
		handle = USER32.GetClipboardData(CF_UNICODETEXT)
		if not handle:
			return None
		pointer = kernel32.GlobalLock(handle)
		try:
			return ctypes.wstring_at(pointer)
		finally:
			kernel32.GlobalUnlock(handle)
	finally:
		USER32.CloseClipboard()


def set_clipboard_text(text):
	kernel32 = ctypes.windll.kernel32
	kernel32.GlobalAlloc.restype = ctypes.c_void_p
	kernel32.GlobalLock.restype = ctypes.c_void_p
	kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
	kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
	USER32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
	USER32.SetClipboardData.restype = ctypes.c_void_p
	data = ctypes.create_unicode_buffer(text)
	if not USER32.OpenClipboard(None):
		raise OSError("OpenClipboard failed")
	try:
		USER32.EmptyClipboard()
		handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, ctypes.sizeof(data))
		pointer = kernel32.GlobalLock(handle)
		ctypes.memmove(pointer, data, ctypes.sizeof(data))
		kernel32.GlobalUnlock(handle)
		if not USER32.SetClipboardData(CF_UNICODETEXT, handle):
			raise OSError("SetClipboardData failed")
	finally:
		USER32.CloseClipboard()


def key_event(vk, up=False, layout=None):
	# <!-- custom: Events used to carry no scan code.
	# Civ4, a DirectX game, ignored them while the user's real typing reached its Sevopedia search box, so each event now carries the scan code a real key press has. (Claude Code Opus 5.5) -->
	flags = (KEYEVENTF_KEYUP if up else 0) | (KEYEVENTF_EXTENDEDKEY if vk in EXTENDED_KEYS else 0)
	scan = USER32.MapVirtualKeyExW(vk, 0, layout) if layout else USER32.MapVirtualKeyW(vk, 0)
	USER32.keybd_event(vk, scan, flags, 0)


def tap(vk, modifiers=(), layout=None):
	# <!-- custom: Release pressed keys in finally, without another delay that could interrupt cleanup. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
	pressed = []
	try:
		for modifier in modifiers:
			key_event(modifier, layout=layout)
			pressed.append(modifier)
			time.sleep(0.04)
		key_event(vk, layout=layout)
		pressed.append(vk)
		time.sleep(0.06)
	finally:
		for held in reversed(pressed):
			key_event(held, up=True, layout=layout)
	time.sleep(0.15)


def paste(pid, x, y, text, send=None):
	# <!-- custom: Click a message box and paste text into it without sending, so the agent can screenshot the box before pressing Enter with the key command.
	# Replaces the one-off keys.ps1 script the first Codex message used.
	# Keystrokes reached the Codex app on 2026-11-10 but not Civ4, whose DirectX input ignores them.
	# Pasting does not clear the box: a draft the user left there would be sent with the message, so check the box in a screenshot first.
	# The user's clipboard text is restored afterwards; a non-text clipboard, such as an image, is not.
	# The clipboard is replaced only after click's checks pass, so a refused click leaves it untouched, as Codex's 2026-11-10 review asked. (Claude Code Opus 5.5) -->
	# <!-- custom: Pasting must bring the window to the front, so keys the user types meanwhile land there: on 2026-11-10, while the user typed in the Claude app, two pastes into Codex arrived with stray letters before the header ("nd", "i s"), although the box was empty just before.
	# So send (Enter in the same focus grab) shortens the time away from the user's window, and focus goes back to the window that was in front, shrinking the gap to about a second; the message header and Reply: line let the recipient spot what still slips in. (Claude Code Opus 5.5) -->
	previous = USER32.GetForegroundWindow()
	saved = clipboard_text()
	point = click(pid, x, y)
	set_clipboard_text(text)
	try:
		# <!-- custom: The target must still be in front before the paste and again before Enter: on 2026-11-26 the user moved the mouse just as agent_message.py pasted into Codex, the message never reached Codex, and its text and Enter went to whichever window took focus.
		# The idle wait before the send cannot cover the second or so the click, paste and Enter take, so this stops the send instead of letting it land elsewhere. (Claude Code Opus 5.5) -->
		if window_pid(USER32.GetForegroundWindow()) != pid:
			raise RuntimeError("the target window lost focus before the paste; nothing was pasted")
		tap(ord("V"), (VK_CONTROL,))
		time.sleep(0.3)
		if send:
			if window_pid(USER32.GetForegroundWindow()) != pid:
				raise RuntimeError("the target window lost focus after the paste; Enter was not pressed, so the text may sit unsent in whichever window took focus")
			tap(*KEYS[send])
	finally:
		if saved is not None:
			set_clipboard_text(saved)
		give_focus_back(previous, pid)
	return point


def user_idle_seconds():
	# <!-- custom: Seconds since the last keyboard or mouse input anywhere on the desktop (GetLastInputInfo).
	# The tool's own clicks and keys count as input too, so read it before acting, not after. (Claude Code Opus 5.5) -->
	class LASTINPUTINFO(ctypes.Structure):
		_fields_ = [("cbSize", wt.UINT), ("dwTime", wt.DWORD)]

	info = LASTINPUTINFO(ctypes.sizeof(LASTINPUTINFO), 0)
	if not USER32.GetLastInputInfo(ctypes.byref(info)):
		raise OSError("GetLastInputInfo failed")
	return ((ctypes.windll.kernel32.GetTickCount() - info.dwTime) & 0xFFFFFFFF) / 1000.0


def wait_for_idle_user(idle_seconds, timeout_seconds):
	# <!-- custom: Wait until nobody has typed or moved the mouse for idle_seconds, so a paste does not mix with the user's typing; return False if that never happens within timeout_seconds. (Claude Code Opus 5.5) -->
	deadline = time.monotonic() + timeout_seconds
	while user_idle_seconds() < idle_seconds:
		if time.monotonic() > deadline:
			return False
		time.sleep(0.25)
	return True


def give_focus_back(previous, pid):
	# <!-- custom: Return focus to the window that was in front before paste or key took it, usually the user's, unless that was the target itself. (Claude Code Opus 5.5) -->
	if previous and window_pid(previous) not in (0, pid):
		bring_to_front(previous, window_pid(previous), allow_click=False)


NAMED_VKS = {"enter": 0x0D, "esc": 0x1B, "backspace": 0x08, "tab": 0x09, "space": 0x20, "left": 0x25, "up": 0x26, "right": 0x27, "down": 0x28,
	"pgup": 0x21, "pgdn": 0x22, "home": 0x24, "end": 0x23, "insert": 0x2D, "delete": 0x2E, "pause": 0x13}
# <!-- custom: Number pad keys num0 to num9 move units in Civ4 (num5 centres or cycles), so they are named too. (Claude Code Opus 5.5) -->
NAMED_VKS.update({"num%d" % n: 0x60 + n for n in range(10)})
# <!-- custom: Civ4's unit cycling uses comma, period, backslash and slash; these are the US-layout VK_OEM codes, which another keyboard layout can place elsewhere. (Claude Code Opus 5.5) -->
NAMED_VKS.update({"comma": 0xBC, "period": 0xBE, "backslash": 0xDC, "slash": 0xBF})
# <!-- custom: 'key escape' failed with "unknown key 'escape'" while closing Civ4's Victory screen (2026-11-15), as only the short name esc was known; the usual long names are aliases now, and the error lists the names it knows. (Claude code Opus 5.5) -->
NAMED_VKS.update({"escape": 0x1B, "return": 0x0D, "del": 0x2E, "ins": 0x2D, "pageup": 0x21, "pagedown": 0x22})
# <!-- custom: Print Screen makes Civ4 save its own Civ4ScreenShotNNNN.JPG in My Games' ScreenShots, the small JPG the repository's screenshots use; 'key printscreen' failed as unknown while taking Debug Info screen shots (2026-11-23). (Claude code Opus 5.5) -->
NAMED_VKS.update({"printscreen": 0x2C, "prtsc": 0x2C})
MODIFIER_VKS = {"ctrl": VK_CONTROL, "shift": 0x10, "alt": 0x12}
# <!-- custom: Each printable ASCII character as the US-keyboard key and Shift state that types it, for type --us-keys; see type_text. (Claude Code Opus 5.5) -->
US_KEYS = {" ": (0x20, False)}
for _unshifted, _shifted, _vk in zip("0123456789-=[]\\;',./`", ")!@#$%^&*(_+{}|:\"<>?~", (0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0xBD, 0xBB, 0xDB, 0xDD, 0xDC, 0xBA, 0xDE, 0xBC, 0xBE, 0xBF, 0xC0)):
	US_KEYS[_unshifted] = (_vk, False)
	US_KEYS[_shifted] = (_vk, True)
for _letter in "abcdefghijklmnopqrstuvwxyz":
	US_KEYS[_letter] = (ord(_letter.upper()), False)
	US_KEYS[_letter.upper()] = (ord(_letter.upper()), True)


def parse_key(name):
	# <!-- custom: Any combination such as ctrl+shift+x, f10 or ctrl+left, so the Civ4 shortcuts listed in civ4_ui_map.json can all be sent; the fixed KEYS list covered only the few keys the agent apps needed. (Claude Code Opus 5.5) -->
	if name in KEYS:
		return KEYS[name]
	parts = name.lower().split("+")
	modifiers = tuple(MODIFIER_VKS[p] for p in parts[:-1])
	last = parts[-1]
	if last in NAMED_VKS:
		vk = NAMED_VKS[last]
	elif len(last) == 1 and last.isalnum():
		vk = ord(last.upper())
	elif last.startswith("f") and last[1:].isdigit() and 1 <= int(last[1:]) <= 12:
		vk = 0x6F + int(last[1:])
	else:
		raise ValueError("unknown key %r; use a letter or digit, f1 to f12, one of %s, optionally after ctrl+, shift+ or alt+" % (name, ", ".join(sorted(NAMED_VKS))))
	return vk, modifiers


def key(pid, name, hold=0.0, count=1):
	# <!-- custom: Count repeats a key during one focus grab, and hold gives a game time to read the input before focus returns. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
	# <!-- custom: Press one key, such as Enter to send a pasted message, after checking the window is in front, as click does. (Claude Code Opus 5.5) -->
	hwnd = find_window(pid)
	if hwnd is None:
		raise RuntimeError("no visible window for process %d" % pid)
	previous = USER32.GetForegroundWindow()
	if window_pid(bring_to_front(hwnd, pid)) != pid:
		raise RuntimeError("process %d's window did not come to the front" % pid)
	try:
		for _ in range(count):
			tap(*parse_key(name))
		# <!-- custom: A game reads input on its own frames, so hold the focus a moment before giving it back, or a key can arrive after the window is no longer in front. (Claude Code Opus 5.5) -->
		time.sleep(hold)
	finally:
		give_focus_back(previous, pid)


def type_text(pid, text, hold=0.5, us_keys=False):
	# <!-- custom: Type text as key presses with scan codes, for a game such as Civ4 that does not take pasted text. (Claude Code Opus 5.5) -->
	# <!-- custom: us_keys selects printable ASCII for Sevopedia's US-style key handling.
	# Check the whole string first because switching to layout-based input partway could type different characters there. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
	if us_keys and any(character not in US_KEYS for character in text):
		raise ValueError("--us-keys accepts only printable ASCII")
	hwnd = find_window(pid)
	if hwnd is None:
		raise RuntimeError("no visible window for process %d" % pid)
	# <!-- custom: Was letters, digits and spaces only; with the layout lookup below, any character the keyboard can type is accepted. (Claude Code Opus 5.5) -->
	for character in text:
		if not character.isprintable():
			raise ValueError("type supports printable characters only, not %r" % character)
	previous = USER32.GetForegroundWindow()
	foreground = bring_to_front(hwnd, pid)
	if window_pid(foreground) != pid:
		raise RuntimeError("process %d's window did not come to the front" % pid)
	try:
		# <!-- custom: Use the focused window thread's layout because the helper can have a different one.
		# On French AZERTY, typing 2 requires Shift. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
		USER32.VkKeyScanExW.restype = ctypes.c_short
		USER32.VkKeyScanExW.argtypes = [wt.WCHAR, ctypes.c_void_p]
		USER32.GetKeyboardLayout.restype = ctypes.c_void_p
		USER32.MapVirtualKeyExW.argtypes = [wt.UINT, wt.UINT, ctypes.c_void_p]
		layout = USER32.GetKeyboardLayout(USER32.GetWindowThreadProcessId(foreground, None))
		if not layout:
			raise OSError("could not read the target window's keyboard layout")
		for character in text:
			# <!-- custom: Civ4's own text boxes follow the Windows layout: on French AZERTY the Ctrl+Shift+X turn box showed "é" for an unshifted 2 key, hence the layout lookup below.
			# The Sevopedia search box, read by our Python from key codes, maps them as a US keyboard would: there the lookup's Shift+2 showed "@" and "-" showed "6".
			# --us-keys sends ASCII as US keys for such fields. (Claude Code Opus 5.5) -->
			if us_keys:
				vk, shifted = US_KEYS[character]
				tap(vk, (0x10,) if shifted else (), layout)
				continue
			# <!-- custom: ctypes expects a character once the argument is declared as WCHAR; passing ord(character) raised TypeError before typing. (GPT-6.1-Sol) -->
			scan = USER32.VkKeyScanExW(character, layout)
			if scan == -1:
				raise ValueError("no key for %r on this keyboard layout" % character)
			tap(scan & 0xFF, tuple(vk for bit, vk in ((0x100, 0x10), (0x200, VK_CONTROL), (0x400, 0x12)) if scan & bit), layout)
		time.sleep(hold)
	finally:
		give_focus_back(previous, pid)


def request_close(pid):
	# <!-- custom: WM_CLOSE is what the title bar's X sends; Civ4 exited with code 0 and no confirmation dialog when tested in game. (Claude Code Opus 5.5) -->
	hwnd = find_window(pid)
	if hwnd is None:
		return False
	return bool(USER32.PostMessageW(hwnd, WM_CLOSE, 0, 0))


DUMP_FILE = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "Civ4BeyondSword.exe.dmp"
DUMP_BUTTONS = {"full": "Full Dump", "normal": "Normal Dump"}


def find_button(pid, label, title_prefix=None):
	# <!-- custom: The button of that label in any top-level window of pid, such as the crash prompt's "Full Dump", or None. (Claude code Opus 5.5) -->
	# <!-- custom: Or, with pid None, in a visible top-level window whose title starts with title_prefix, whatever its process: the Save As dialog the Claude app opens for each browser-pane download belongs to one of its many processes, and its title is the download's URL (2026-11-23). (Claude code Opus 5.5) -->
	found = []
	proc_type = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

	# <!-- custom: WM_GETTEXT with a timeout, as Microsoft recommends for another process's controls, and the class checked, so a hung dialog or a same-named label cannot be taken for the button (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	def child(hwnd, _lparam):
		class_name = ctypes.create_unicode_buffer(64)
		USER32.GetClassNameW(hwnd, class_name, 64)
		if class_name.value.lower() != "button":
			return True
		buffer = ctypes.create_unicode_buffer(128)
		result = ctypes.c_size_t()
		if USER32.SendMessageTimeoutW(hwnd, 0x000D, 128, buffer, 0x0002, 1000, ctypes.byref(result)) and buffer.value.replace("&", "") == label:
			found.append(hwnd)
		return True

	def top(hwnd, _lparam):
		owner = wt.DWORD()
		USER32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
		if owner.value == pid if pid is not None else (USER32.IsWindowVisible(hwnd) and window_title(hwnd).startswith(title_prefix)):
			USER32.EnumChildWindows(hwnd, proc_type(child), 0)
		return True

	USER32.EnumWindows(proc_type(top), 0)
	return found[0] if found else None


def visible_windows(predicate):
	found = []
	proc_type = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

	def collect(hwnd, _lparam):
		if USER32.IsWindowVisible(hwnd) and predicate(hwnd):
			found.append(hwnd)
		return True

	USER32.EnumWindows(proc_type(collect), 0)
	return found


def window_class(hwnd):
	buffer = ctypes.create_unicode_buffer(64)
	USER32.GetClassNameW(hwnd, buffer, 64)
	return buffer.value


def save_download(title_prefix, timeout=15.0, expect=None, folder=Path.home() / "Downloads"):
	# <!-- custom: Saves a browser-pane download: the Claude app opens Windows' Save As dialog for each one, titled with the download's URL, and the app waits on it until someone answers (2026-11-23, the user's screenshot).
	# Pressing Save by its label worked, but when the name already existed Windows asked whether to replace the file, so one press was not enough (the user's question); the first version stopped there and left the prompt open, blocking the app.
	# Save goes by its standard ID, IDOK, so a French "Enregistrer" needs no label. (Claude code Opus 5.5) -->
	IDOK, WM_COMMAND, WM_GETTEXT, WM_SETTEXT, GW_OWNER = 1, 0x0111, 0x000D, 0x000C, 4
	deadline = time.monotonic() + timeout
	dialogs = []
	while not dialogs and time.monotonic() < deadline:
		dialogs = visible_windows(lambda hwnd: window_class(hwnd) == "#32770" and window_title(hwnd).startswith(title_prefix))
		if not dialogs:
			time.sleep(0.5)
	if not dialogs:
		raise SystemExit("no Save As dialog titled %r... appeared" % title_prefix)
	seen = time.monotonic()
	dialog = dialogs[0]
	# <!-- custom: The name box is searched among all descendants: the Explorer-style dialog nests it, so GetDlgItem(dialog, 1148) found nothing, the first run read an empty name and its renames went nowhere.
	# A dump of the real dialog (2026-11-23) showed why: its name box is a ComboBox with ID 0 inside a FloatNotifySink, holding an Edit with ID 1001, while the file type ComboBox beside it has no Edit; 1148 stays for the classic dialog. (Claude code Opus 5.5) -->
	boxes = []
	proc_type = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

	def find_box(hwnd, _lparam):
		parent = USER32.GetParent(hwnd)
		if window_class(hwnd) == "Edit" and window_class(parent) == "ComboBox" and (USER32.GetDlgCtrlID(parent) == 1148 or window_class(USER32.GetParent(parent)) == "FloatNotifySink"):
			boxes.append(hwnd)
		return True

	USER32.EnumChildWindows(dialog, proc_type(find_box), 0)
	name_box = boxes[0] if boxes else None
	if not name_box:
		raise SystemExit("found the Save As dialog but not its file name box; left for the user")
	buffer = ctypes.create_unicode_buffer(1024)
	USER32.SendMessageW(name_box, WM_GETTEXT, 1024, buffer)
	original = buffer.value
	if not original:
		raise SystemExit("the Save As dialog's file name reads empty; left for the user")
	# <!-- custom: A dialog takes focus on opening, so the user's typing can replace its name: a Drive folder ZIP took seconds to prepare, its dialog opened after the click that wait-idle guarded, and "he" was saved as he.zip (2026-11-23).
	# Codex's review found that a check of input since the dialog was first seen misses typing before that, so the caller names the file it asked for with expect, the name Drive shows, and any other name stops here. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if expect is not None and original.casefold() != expect.casefold():
		raise SystemExit("the Save As dialog names %r, not the expected %r, perhaps typed over while it had focus; left for the user" % (original, expect))
	stem, dot, extension = original.rpartition(".")
	if not dot:
		stem, extension = original, ""
	# <!-- custom: A free name is chosen before Save, so no replace prompt comes up, and a name already there gets the local time, "name_20261123T091234.ext", which is unique and says when the copy came (the user's idea, over browsers' "name (1).ext").
	# The first versions answered the prompt instead and failed twice: posting IDNO did nothing, as the prompt is a task dialog whose Yes and No buttons both have ID 0, and the Save dialog behind it turns hidden and disabled, not closed, which was read as saved (2026-11-23).
	# The name box gets the absolute path, as Codex's review noted that a bare name is relative to whatever folder the dialog shows, so checking Downloads alone could miss a clash; exists() follows Windows' case rules there. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	target = Path(folder) / original
	if target.exists():
		target = target.with_name("%s_%s%s" % (stem, time.strftime("%Y%m%dT%H%M%S"), dot + extension))
		if target.exists():
			raise SystemExit("%r and %s both exist; left for the user" % (original, target))
	USER32.SendMessageW(name_box, WM_SETTEXT, 0, ctypes.c_wchar_p(str(target)))
	USER32.SendMessageW(name_box, WM_GETTEXT, 1024, buffer)
	if buffer.value != str(target):
		raise SystemExit("could not set the download's path to %s; left for the user" % target)
	# <!-- custom: Input checked again just before Save, not only once: a key pressed after the name was set would land in the box (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if user_idle_seconds() < time.monotonic() - seen:
		raise SystemExit("the keyboard or mouse was used while the Save As dialog was open, so its name may be the user's; left for the user")
	USER32.PostMessageW(dialog, WM_COMMAND, IDOK, 0)
	end = time.monotonic() + 15.0
	while USER32.IsWindow(dialog) and time.monotonic() < end:
		# <!-- custom: A prompt should not come up now; if one does, it is left open, as its buttons have no IDs and the last one was only assumed to be No (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		if visible_windows(lambda hwnd: hwnd != dialog and window_class(hwnd) == "#32770" and USER32.GetWindow(hwnd, GW_OWNER) == dialog):
			raise SystemExit("Windows put up a prompt over the Save As dialog for %s; left for the user" % target)
		time.sleep(0.25)
	if USER32.IsWindow(dialog):
		raise SystemExit("pressed Save, but the dialog still exists, perhaps hidden; left for the user")
	# <!-- custom: Success is this exact file arriving, not any new file in the folder, which Codex's review showed an unrelated download could pass. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	while time.monotonic() < end and not target.exists():
		time.sleep(0.25)
	if not target.exists():
		raise SystemExit("the dialog closed, but %s did not appear" % target)
	return target


def minidump_pid(path):
	# <!-- custom: The process ID a minidump records in its MiscInfo stream (type 15; ProcessId at offset 8 when Flags1 has bit 1), or None.
	# 'dump' checks it, as every Civ4 writes the same file name (Codex's review). See KI#1089. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	with open(path, "rb") as stream:
		header = stream.read(32)
		if header[:4] != b"MDMP":
			return None
		count, directory = struct.unpack_from("<II", header, 8)
		stream.seek(directory)
		entries = stream.read(12 * count)
		for i in range(count):
			kind, size, rva = struct.unpack_from("<III", entries, 12 * i)
			if kind == 15 and size >= 12:
				stream.seek(rva)
				flags, process_id = struct.unpack_from("<II", stream.read(12), 4)
				return process_id if flags & 1 else None
	return None


def save_dump(pid, kind="full", timeout=300.0):
	# <!-- custom: At KI#1088's crash prompt (2026-11-13) a full dump took three tries: clicking by window coordinates, then two wait loops that started PowerShell on each pass and showed nothing for minutes.
	# This presses the button by its label with BM_CLICK, which needs no focus or coordinates, then waits for the file to be finished, about a dozen seconds for 1.38 GB.
	# BM_CLICK can fail on an inactive dialog (Microsoft's documentation, as Codex noted); the timeout then reports no dump rather than a stale one.
	# Not yet tried on a real prompt.
	# A full dump is the user's rule (README_DLL_Debugging.md): a normal one lacks the heap. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	button = find_button(pid, DUMP_BUTTONS[kind])
	if button is None:
		raise SystemExit("no %r button in process %d's windows; is the crash prompt up?" % (DUMP_BUTTONS[kind], pid))
	# <!-- custom: Codex's review: the first version accepted a file from just before the press and took two equal sizes for the end, which a pause in writing also gives.
	# Now the file must differ from its state before the press, and it is done once it can be opened without sharing writes, which fails while the writer still holds it.
	# The name is shared by every Civ4, so a second client's crash would replace it. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	before = None
	if DUMP_FILE.exists():
		stat = DUMP_FILE.stat()
		before = (stat.st_mtime, stat.st_size)
	if not USER32.PostMessageW(button, 0x00F5, 0, 0):
		raise SystemExit("could not send the click to %r: Windows error %d" % (DUMP_BUTTONS[kind], ctypes.GetLastError()))
	deadline = time.monotonic() + timeout
	while time.monotonic() < deadline:
		time.sleep(2.0)
		if not DUMP_FILE.exists():
			continue
		stat = DUMP_FILE.stat()
		if (stat.st_mtime, stat.st_size) == before or stat.st_size == 0:
			continue
		kernel32 = ctypes.windll.kernel32
		# <!-- custom: A handle is pointer-sized, so the restype is set, as for the clipboard calls above. (Claude code Opus 5.5) -->
		kernel32.CreateFileW.restype = ctypes.c_void_p
		kernel32.CreateFileW.argtypes = [wt.LPCWSTR, wt.DWORD, wt.DWORD, ctypes.c_void_p, wt.DWORD, wt.DWORD, ctypes.c_void_p]
		kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
		handle = kernel32.CreateFileW(str(DUMP_FILE), 0x80000000, 0x00000001, None, 3, 0, None)
		if handle is None or handle == ctypes.c_void_p(-1).value:
			continue
		# <!-- custom: While this handle denies writing, no other Civ4 can replace the file, so its process ID is checked and it is copied under a name of its own before the handle is let go; the first version closed the handle and then read the size, which could have been a replacement's (Codex's review). See KI#1089. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		try:
			dump_pid = minidump_pid(DUMP_FILE)
			if dump_pid != pid:
				raise SystemExit("the dump at %s is from process %s, not %d" % (DUMP_FILE, dump_pid, pid))
			kept = DUMP_FILE.with_name("Civ4BeyondSword_%d_%s.dmp" % (pid, time.strftime("%Y%m%dT%H%M%S")))
			shutil.copyfile(DUMP_FILE, kept)
		finally:
			kernel32.CloseHandle(handle)
		return kept, kept.stat().st_size
	raise SystemExit("no finished dump at %s within %g s" % (DUMP_FILE, timeout))


# <!-- custom: Native process probes, with explicit prototypes so handles keep their full width. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
_KERNEL32 = ctypes.WinDLL("kernel32", use_last_error=True)
_KERNEL32.OpenProcess.argtypes = (wt.DWORD, wt.BOOL, wt.DWORD)
_KERNEL32.OpenProcess.restype = wt.HANDLE
_KERNEL32.GetExitCodeProcess.argtypes = (wt.HANDLE, ctypes.POINTER(wt.DWORD))
_KERNEL32.GetExitCodeProcess.restype = wt.BOOL
_KERNEL32.WaitForSingleObject.argtypes = (wt.HANDLE, wt.DWORD)
_KERNEL32.WaitForSingleObject.restype = wt.DWORD
_KERNEL32.TerminateProcess.argtypes = (wt.HANDLE, wt.UINT)
_KERNEL32.TerminateProcess.restype = wt.BOOL
_KERNEL32.GetProcessTimes.argtypes = (wt.HANDLE, ctypes.POINTER(wt.FILETIME), ctypes.POINTER(wt.FILETIME), ctypes.POINTER(wt.FILETIME), ctypes.POINTER(wt.FILETIME))
_KERNEL32.GetProcessTimes.restype = wt.BOOL
_KERNEL32.QueryFullProcessImageNameW.argtypes = (wt.HANDLE, wt.DWORD, wt.LPWSTR, ctypes.POINTER(wt.DWORD))
_KERNEL32.QueryFullProcessImageNameW.restype = wt.BOOL
_KERNEL32.CloseHandle.argtypes = (wt.HANDLE,)
_KERNEL32.CloseHandle.restype = wt.BOOL
_PROCESS_TERMINATE = 0x0001
_PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
_SYNCHRONIZE = 0x00100000
_STILL_ACTIVE = 259
_WAIT_OBJECT_0 = 0
_WAIT_TIMEOUT = 0x102
_ERROR_INVALID_PARAMETER = 87


def _handle_state(handle):
	# <!-- custom: running, exiting (the exit code is set but the handle has not signaled: a client hung at exit, KI#1102), gone, or unknown when a call fails. (Claude code Opus 5.5) -->
	wait = _KERNEL32.WaitForSingleObject(handle, 0)
	if wait == _WAIT_OBJECT_0:
		return "gone"
	if wait != _WAIT_TIMEOUT:
		return "unknown"
	code = wt.DWORD()
	if not _KERNEL32.GetExitCodeProcess(handle, ctypes.byref(code)):
		return "unknown"
	return "running" if code.value == _STILL_ACTIVE else "exiting"


def _creation_time(handle):
	times = [wt.FILETIME() for _ in range(4)]
	if not _KERNEL32.GetProcessTimes(handle, *[ctypes.byref(time_) for time_ in times]):
		return None
	return (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime


def _image_name(handle):
	size = wt.DWORD(1024)
	buffer = ctypes.create_unicode_buffer(size.value)
	if not _KERNEL32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
		return None
	return buffer.value.rsplit("\\", 1)[-1]


def process_state(pid):
	# <!-- custom: running, exiting, gone or unknown, from a handle of the process rather than its exit code alone: that code read 0 for a client hung at exit (KI#1102), so close reported it exited while it stayed and kept Civ4's single-instance lock (2026-11-26).
	# An access-denied open is unknown, not gone, as Codex's review (GPT-6.2-Sol) found the first version took any failed open or wait for an exit. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	handle = _KERNEL32.OpenProcess(_PROCESS_QUERY_LIMITED_INFORMATION | _SYNCHRONIZE, False, pid)
	if not handle:
		return "gone" if ctypes.get_last_error() == _ERROR_INVALID_PARAMETER else "unknown"
	try:
		return _handle_state(handle)
	finally:
		_KERNEL32.CloseHandle(handle)


def process_alive(pid):
	# <!-- custom: True while the process runs, or when its state cannot be read; a client hung at exit has quit its game, so callers waiting for a game to end treat it as ended, and close ends it on --force. (Claude code Opus 5.5) -->
	return process_state(pid) in ("running", "unknown")


def process_identity(pid):
	# <!-- custom: (image name, creation time) of a live or exiting process, None when it cannot be read, so a caller can check that a pid still names the process it found before acting on it. (Claude code Opus 5.5) -->
	handle = _KERNEL32.OpenProcess(_PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
	if not handle:
		return None
	try:
		return (_image_name(handle), _creation_time(handle))
	finally:
		_KERNEL32.CloseHandle(handle)


def terminate_process(pid, wait_ms=5000, expect=None, only_exiting=False):
	# <!-- custom: Ends a process with TerminateProcess on a handle of its own and waits for that handle to signal; returns (ended, message).
	# On 2026-11-26 Stop-Process, taskkill /F and an elevated Stop-Process through a scheduled task left a client hung at exit (KI#1102) in place, whether or not they reached TerminateProcess, which was not traced; Codex (GPT-6.2-Sol) then ended it this way from a non-elevated shell.
	# expect, an identity from process_identity, and only_exiting are checked on the same handle before the call, as a pid freed between finding a process and ending it can name another one (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	handle = _KERNEL32.OpenProcess(_PROCESS_TERMINATE | _PROCESS_QUERY_LIMITED_INFORMATION | _SYNCHRONIZE, False, pid)
	if not handle:
		error = ctypes.get_last_error()
		if error == _ERROR_INVALID_PARAMETER:
			return True, "process %d is already gone" % pid
		return False, "could not open process %d (error %d)" % (pid, error)
	try:
		state = _handle_state(handle)
		if state == "gone":
			return True, "process %d had already ended" % pid
		if expect is not None and (_image_name(handle), _creation_time(handle)) != expect:
			return False, "process %d is no longer the one found; left alone" % pid
		if only_exiting and state != "exiting":
			return False, "process %d is %s, not hung at exit; left alone" % (pid, state)
		if not _KERNEL32.TerminateProcess(handle, 1):
			error = ctypes.get_last_error()
			if _KERNEL32.WaitForSingleObject(handle, 0) == _WAIT_OBJECT_0:
				return True, "process %d ended" % pid
			return False, "TerminateProcess failed on process %d (error %d)" % (pid, error)
		if _KERNEL32.WaitForSingleObject(handle, wait_ms) == _WAIT_OBJECT_0:
			return True, "process %d ended" % pid
		return False, "process %d did not end within %d ms of TerminateProcess" % (pid, wait_ms)
	finally:
		_KERNEL32.CloseHandle(handle)


def _civ4_candidates():
	# <!-- custom: [(pid, command line)] of every Civ4 process Windows lists, from one CIM query; Get-Process could not find a client hung at exit in Codex's shell while CIM and tasklist listed it (2026-11-26), so each candidate is then probed natively. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	command = "Get-CimInstance Win32_Process -Filter \"Name='%s'\" | ForEach-Object { \"$($_.ProcessId)`t$($_.CommandLine)\" }" % EXE_NAME
	output = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True, text=True, check=True).stdout
	result = []
	for line in output.splitlines():
		if "\t" in line:
			pid, cmd = line.split("\t", 1)
			result.append((int(pid), cmd))
	return result


def stuck_civ4_processes():
	# <!-- custom: Return the pids of Civ4 clients hung at exit, a waiting steamclient frame in the dumps (KI#1102), which stay listed and, as inferred from a client started with Civ4's multiple argument running beside one, hold Civ4's single-instance lock.
	# Found on 2026-11-26; terminate_process ends one.
	# See README_Game_Runs.md, "A client that will not go away". (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	return [pid for pid, _ in stuck_civ4_clients()]


def stuck_civ4_clients():
	# <!-- custom: [(pid, identity)] of Civ4 clients hung at exit, the identity read on the same handle that showed the pending exit and the Civ4 image, for terminate_process(expect=...).
	# Codex's review (GPT-6.2-Sol) found that reading it on a later handle could identify a process that reused the pid meanwhile. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	result = []
	for pid, _ in _civ4_candidates():
		handle = _KERNEL32.OpenProcess(_PROCESS_QUERY_LIMITED_INFORMATION | _SYNCHRONIZE, False, pid)
		if not handle:
			continue
		try:
			if _handle_state(handle) != "exiting":
				continue
			identity = (_image_name(handle), _creation_time(handle))
			if identity[0] and identity[0].lower() == EXE_NAME.lower() and identity[1] is not None:
				result.append((pid, identity))
		finally:
			_KERNEL32.CloseHandle(handle)
	return result


def civ4_processes():
	# <!-- custom: Return [(pid, command line)] for every running Civ4 client. (Claude Code Opus 5.5) -->
	# <!-- custom: A client hung at exit (KI#1102) stays listed and is left out, as it runs no game: on 2026-11-26 one made start_game.py refuse to start another.
	# One whose state cannot be read counts as running. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	return [(pid, cmd) for pid, cmd in _civ4_candidates() if process_state(pid) in ("running", "unknown")]


# <!-- custom: Python and XML saved under Assets while an AdvCiv-SAS client runs break that game, so an agent closes such clients first; on 2026-11-20 an agent edited advisor Python while the user's own client ran, which the user said agents should simply close themselves.
# --mod picks every client of that mod, whose command line ends in mod=\<name>, so a client of another mod is left alone; a stuck client once ignored WM_CLOSE, hence --force after --wait. (Claude Code Opus 5.5) -->
# <!-- custom: A client's mod is its mod= argument, or for an agent-started client the Mod line of its ini= file, as SASPilot and run_autoplay.py pass no mod=: the first --mod matched only mod= and missed them (2026-11-20). (Claude Code Opus 5.5) -->
def client_mod(cmd):
	m = re.search(r'"mod=\\?([^"]+)"|mod=\\?(\S+)', cmd, re.IGNORECASE)
	if m:
		return m.group(1) or m.group(2)
	m = re.search(r'ini="?([^" ]+)', cmd, re.IGNORECASE)
	if m:
		ini = DEFAULT_CIV4_DIR / m.group(1)
		if ini.exists():
			line = re.search(r'(?mi)^\s*mod\s*=\s*(.+?)\s*$', ini.read_bytes().decode('latin-1'))
			if line:
				return line.group(1).split('\\')[-1]
	return ''


def close_clients(pid, mod, wait, force):
	if pid is not None:
		pids = [pid]
	else:
		pids = [p for (p, cmd) in civ4_processes() if client_mod(cmd).lower() == mod.lower()]
		if not pids:
			print("no Civ4 client running %s" % mod)
			return
	for p in pids:
		if not request_close(p):
			print("no window for process %d" % p)
		else:
			print("WM_CLOSE sent to %d" % p)
	# <!-- custom: An exit passes through "exiting" while DLLs unload and may write their last logs, so a client counts as hung at exit (KI#1102) only once it has been exiting for 15 s. (Claude code Opus 5.5) -->
	deadline = time.time() + wait
	exiting_since = {}
	while wait > 0 and time.time() < deadline:
		waiting = False
		for p in pids:
			state = process_state(p)
			if state == "exiting":
				exiting_since.setdefault(p, time.time())
				waiting = waiting or time.time() - exiting_since[p] < 15
			elif state != "gone":
				waiting = True
		if not waiting:
			break
		time.sleep(0.5)
	for p in pids:
		state = process_state(p)
		if state == "gone":
			if wait > 0:
				print("process %d exited" % p)
		# <!-- custom: A client that quit but hangs at exit (KI#1102) was reported exited on 2026-11-26 while it stayed listed; it is reported as such, and ended on --force. (Claude code Opus 5.5) -->
		elif state == "exiting" and not force:
			if wait > 0:
				print("process %d quit its game but is hung at exit (KI#1102); add --force to end it" % p)
		elif force:
			# <!-- custom: TerminateProcess on a handle of its own, as taskkill /F left a client hung at exit (KI#1102) in place on 2026-11-26. (Claude code Opus 5.5) -->
			ended, message = terminate_process(p)
			if not ended:
				sys.exit("%s; ask the user to end it in Task Manager" % message)
			print("process %d was %s after %g s; %s" % (p, state, wait, message))
		elif wait > 0:
			sys.exit("process %d still runs after %g s; add --force to end it" % (p, wait))


def launch_detached(arguments, civ4_dir=DEFAULT_CIV4_DIR):
	# <!-- custom: Start Civ4 through WMI so it is not a child of the caller: an agent stopping its shell command once killed the game and its Runtime observers with it. (Claude Code Opus 5.5) -->
	exe = Path(civ4_dir) / EXE_NAME
	command_line = '"%s" %s' % (exe, arguments)
	ps = "$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $env:SAS_LAUNCH_CMD; CurrentDirectory = $env:SAS_LAUNCH_DIR }; \"$($r.ReturnValue) $($r.ProcessId)\""
	env = dict(__import__("os").environ, SAS_LAUNCH_CMD=command_line, SAS_LAUNCH_DIR=str(civ4_dir))
	output = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, check=True, env=env).stdout.split()
	if len(output) != 2 or output[0] != "0":
		raise RuntimeError("Win32_Process.Create failed: %s" % " ".join(output))
	return int(output[1])


def usage_geometry(pid, name, layout_name, kind):
	# <!-- custom: Desktop usage positions move with panels even at the same size, so choose a measured layout explicitly.
	# Check the target title and exact outer size before using a saved point or crop. (GPT-6.1-Sol) -->
	path = Path(__file__).resolve().parent / "layouts" / "app_layouts.json"
	layouts = json.loads(path.read_text(encoding="utf-8"))["usage"]["layouts"]
	layout = layouts.get(layout_name)
	if layout is None:
		sys.exit("unknown usage layout %r; known: %s" % (layout_name, ", ".join(sorted(layouts))))
	hwnd = find_window(pid)
	if hwnd is None:
		sys.exit("no window for process %d" % pid)
	left, top, right, bottom = window_rect(hwnd)
	size = [right - left, bottom - top]
	if window_title(hwnd) != layout["title"] or size != layout["window"]:
		sys.exit("usage layout %s requires the %s window at %dx%d; process %d has a %dx%d window" %
			(layout_name, layout["title"], *layout["window"], pid, *size))
	entries = layout[kind]
	if name not in entries:
		sys.exit("no %s named %r in %s; known: %s" % (kind[:-1], name, layout_name, ", ".join(sorted(entries))))
	return tuple(entries[name])


def named_point(pid, name):
	# <!-- custom: Civ4 click points were first read off screenshots and passed as numbers, then forgotten or re-measured.
	# On 2026-11-11 the user suggested keeping them as data like the agent apps' app_layouts.json, so they live in civ4_points.json, keyed by the window's outer size.
	# The points are window-relative, so where the window sits on the screen does not matter; a different size, such as another game resolution, fails loudly instead of clicking a wrong spot. (Claude Code Opus 5.5) -->
	# <!-- custom: json was imported here when only named points read it; the module imports it now, as the layout files are read elsewhere too. (Claude code Opus 5.5) -->
	make_dpi_aware()
	hwnd = find_window(pid)
	if hwnd is None:
		sys.exit("no window for process %d" % pid)
	left, top, right, bottom = window_rect(hwnd)
	size = (right - left, bottom - top)
	if "." in name:
		# <!-- custom: SCREEN.CONTROL names come from civ4_ui_map.json, the map of Civ4's screens outside a game, such as single_player.load_game. (Claude Code Opus 5.5) -->
		ui = json.loads((Path(__file__).resolve().parents[1] / "game_runs" / "ui_maps" / "civ4_ui_map.json").read_text(encoding="utf-8"))
		if abs(size[0] - ui["window"][0]) > 20 or abs(size[1] - ui["window"][1]) > 20:
			sys.exit("civ4_ui_map.json was measured on a %dx%d window, not %dx%d" % (ui["window"][0], ui["window"][1], size[0], size[1]))
		screen_name, control = name.split(".", 1)
		screen = ui["screens"].get(screen_name)
		if screen is None or control not in screen["controls"]:
			sys.exit("no control %r in civ4_ui_map.json" % name)
		return tuple(screen["controls"][control]["xy"])
	data = json.loads((Path(__file__).resolve().parents[1] / "game_runs" / "ui_maps" / "civ4_points.json").read_text(encoding="utf-8"))
	for layout_name, layout in data["layouts"].items():
		if abs(size[0] - layout["window"][0]) <= 20 and abs(size[1] - layout["window"][1]) <= 20:
			if name not in layout["points"]:
				sys.exit("no point %r in layout %s; known: %s" % (name, layout_name, ", ".join(sorted(layout["points"]))))
			return tuple(layout["points"][name]["xy"])
	sys.exit("no layout in civ4_points.json for a %dx%d window; measure the point on a screenshot and add a layout" % size)


def monitors():
	# <!-- custom: Each monitor's work area (left, top, right, bottom), the screen minus the taskbar, ordered left to right so 1 is the leftmost. (Claude Code Opus 5.5) -->
	make_dpi_aware()

	class MONITORINFO(ctypes.Structure):
		_fields_ = [("cbSize", wt.DWORD), ("rcMonitor", wt.RECT), ("rcWork", wt.RECT), ("dwFlags", wt.DWORD)]

	areas = []
	proc_type = ctypes.WINFUNCTYPE(wt.BOOL, wt.HMONITOR, wt.HDC, ctypes.POINTER(wt.RECT), wt.LPARAM)

	def callback(hmonitor, _hdc, _rect, _lparam):
		info = MONITORINFO()
		info.cbSize = ctypes.sizeof(MONITORINFO)
		USER32.GetMonitorInfoW(hmonitor, ctypes.byref(info))
		work = info.rcWork
		areas.append((work.left, work.top, work.right, work.bottom))
		return True

	USER32.EnumDisplayMonitors(None, None, proc_type(callback), 0)
	return sorted(areas)


def move(pid, monitor, part, size=None, beside=None):
	# <!-- custom: Was move(pid, monitor, part); size and beside serve the topleft and beside parts described below. (Claude code Opus 5.5) -->
	# <!-- custom: Maximized, the Claude and Codex apps each spread a chat column about 1,200 px wide across a 3,840 px 4K window, leaving most of it empty (screenshots of 2026-11-11).
	# On 2026-11-11 the user suggested sharing one monitor between them, half each, to free the other.
	# The window is restored from maximized first.
	# Windows 10 frames carry an invisible resize border, about 11 px on the Claude app, so the visible frame from DWM is placed on the target and the border added around it, as Win+Left and Win+Right do. (Claude Code Opus 5.5) -->
	make_dpi_aware()
	hwnd = find_window(pid)
	if hwnd is None:
		raise OSError("no window for process %d" % pid)
	areas = monitors()
	if not 1 <= monitor <= len(areas):
		raise ValueError("monitor %d not found; this computer has %d" % (monitor, len(areas)))
	left, top, right, bottom = areas[monitor - 1]
	middle = (left + right) // 2
	# <!-- custom: topleft and beside came from watching SASPilot (2026-11-14): halving the 4K screen stretched Civ4 into a 1920x2100 "monster chicken", as the user put it, while the user wanted Civ4 at its own size in the top-left corner and the SASPilotConsole console filling the rest.
	# topleft keeps the window's size (or --size, the visible frame's width and height); beside fills the work area right of another process's window. (Claude Code Opus 5.5) -->
	if part == "beside":
		if beside is None:
			raise ValueError("beside needs --beside <pid>")
		other = find_window(beside)
		if other is None:
			raise OSError("no window for process %d" % beside)
		other_frame = wt.RECT()
		ctypes.windll.dwmapi.DwmGetWindowAttribute(other, 9, ctypes.byref(other_frame), ctypes.sizeof(other_frame))
		target = (min(max(other_frame.right, left), right), right)
	elif part in ("topleft", "bottomleft"):
		target = None
	else:
		target = {"full": (left, right), "maximize": (left, right), "left": (left, middle), "right": (middle, right)}[part]
	USER32.ShowWindow(hwnd, 9)
	frame = wt.RECT()
	ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, 9, ctypes.byref(frame), ctypes.sizeof(frame))
	outer = window_rect(hwnd)
	border_left, border_top = frame.left - outer[0], frame.top - outer[1]
	border_right, border_bottom = outer[2] - frame.right, outer[3] - frame.bottom
	if target is None:
		if size is None:
			size = (frame.right - frame.left, frame.bottom - frame.top)
		target = (left, left + size[0])
		# <!-- custom: bottomleft, the user's ask (2026-11-15), puts a second client started with --multiple under the first one's top-left place, so both stay in view. (Claude code Opus 5.5) -->
		if part == "bottomleft":
			top = bottom - size[1]
		else:
			bottom = top + size[1]
	x = target[0] - border_left
	y = top - border_top
	width = target[1] - target[0] + border_left + border_right
	height = bottom - top + border_top + border_bottom
	# <!-- custom: 0x0014 is SWP_NOZORDER | SWP_NOACTIVATE, so the move neither raises the window nor takes focus from the user. (Claude Code Opus 5.5) -->
	USER32.SetWindowPos(hwnd, None, x, y, width, height, 0x0014)
	# <!-- custom: full only resizes the window over the work area.
	# While an agent tested the Sevopedia at 4K with it, the user noticed the window was not really maximized and showed the difference: a 3838 x 2062 game area against 3840 x 2066 with the title bar's maximize button (2026-11-24).
	# Tests should see the screen a player gets, and a player maximizes, so the user asked for a real maximize, for any monitor size rather than only 4K.
	# maximize first places the window on the chosen monitor, then maximizes it there with ShowWindow's SW_MAXIMIZE (3), which also brings it to the front. (Claude Code Opus 5.5) -->
	if part == "maximize":
		USER32.ShowWindow(hwnd, 3)
	return window_rect(hwnd)


def visible_frame(pid):
	# <!-- custom: The window's visible frame from DWM, without Windows 10's invisible resize border; (left, top, right, bottom). (Claude Code Opus 5.5) -->
	make_dpi_aware()
	hwnd = find_window(pid)
	if hwnd is None:
		raise OSError("no window for process %d" % pid)
	frame = wt.RECT()
	ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, 9, ctypes.byref(frame), ctypes.sizeof(frame))
	return (frame.left, frame.top, frame.right, frame.bottom)


def place_frame(pid, left, top, right, bottom):
	# <!-- custom: Put the window's visible frame exactly on a rectangle, the invisible border added around it as in 'move'; for layouts 'move' has no name for, such as SASPilotConsole.py's bands of one Civ4 and its console per client (2026-11-14). (Claude Code Opus 5.5) -->
	make_dpi_aware()
	hwnd = find_window(pid)
	if hwnd is None:
		raise OSError("no window for process %d" % pid)
	return place_window(hwnd, left, top, right, bottom)


def place_window(hwnd, left, top, right, bottom):
	# <!-- custom: place_frame by window handle, for a window no process ID names reliably: a classic console window belongs to its console host, so SASPilotConsole.py passes GetConsoleWindow()'s handle (Codex's review, 2026-11-14). (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
	make_dpi_aware()
	USER32.ShowWindow(hwnd, 9)
	frame = wt.RECT()
	ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, 9, ctypes.byref(frame), ctypes.sizeof(frame))
	outer = window_rect(hwnd)
	border_left, border_top = frame.left - outer[0], frame.top - outer[1]
	border_right, border_bottom = outer[2] - frame.right, outer[3] - frame.bottom
	USER32.SetWindowPos(hwnd, None, left - border_left, top - border_top, right - left + border_left + border_right, bottom - top + border_top + border_bottom, 0x0014)
	return window_rect(hwnd)


# <!-- custom: Named window layouts, so the agents' and the game's windows can be put back without the user: the user asked to remember the Claude and Codex app positions too, in case they are moved or a layout is changed (2026-11-14).
# Windows are found by their program's file name, as process IDs change with each launch; the Codex desktop app runs as ChatGPT.exe.
# Frames are the visible frames in physical pixels, measured on the user's two 3840x2160 monitors. (Claude Code Opus 5.5) -->
# <!-- custom: Use the shared formatter so each saved window frame and monitor rectangle stays on one line. (GPT-6.1-Sol) -->
POSITIONS_FILE = Path(__file__).resolve().parent / "layouts" / "window_positions.json"
POSITION_APPS = {"claude": "claude.exe", "codex": "ChatGPT.exe", "civ4": "Civ4BeyondSword.exe"}


def image_name(pid):
	handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
	if not handle:
		return None
	try:
		buffer = ctypes.create_unicode_buffer(520)
		size = wt.DWORD(520)
		if not ctypes.windll.kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
			return None
		return os.path.basename(buffer.value)
	finally:
		ctypes.windll.kernel32.CloseHandle(handle)


def app_window(exe):
	# <!-- custom: The largest visible, titled, not minimized top-level window of a program, or None. (Claude Code Opus 5.5) -->
	make_dpi_aware()
	found = []
	proc_type = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

	def callback(hwnd, _):
		if USER32.IsWindowVisible(hwnd) and not USER32.IsIconic(hwnd) and window_title(hwnd):
			name = image_name(window_pid(hwnd))
			if name is not None and name.lower() == exe.lower():
				rect = window_rect(hwnd)
				found.append(((rect[2] - rect[0]) * (rect[3] - rect[1]), hwnd))
		return True

	USER32.EnumWindows(proc_type(callback), 0)
	if not found:
		return None
	return max(found)[1]


def window_by_title(title):
	# <!-- custom: The visible top-level window whose title ends with this, or None: SASPilotConsole windows belong to their console host rather than to the Python that titles them, so they are found by title, e.g. "SASPilotConsole - Civ4 client 12132" (2026-11-15).
	# Ends with rather than equals: a console clicked into goes into selection mode, which pauses its output and prefixes the title with a localized word ("Sélection SASPilotConsole - ..." on the user's French Windows), so the exact title missed that console on the first try. (Claude code Opus 5.5) -->
	make_dpi_aware()
	found = []
	proc_type = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

	def callback(hwnd, _):
		if USER32.IsWindowVisible(hwnd) and window_title(hwnd).endswith(title):
			found.append(hwnd)
		return True

	USER32.EnumWindows(proc_type(callback), 0)
	if not found:
		return None
	return found[0]


def hwnd_frame(hwnd):
	frame = wt.RECT()
	ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, 9, ctypes.byref(frame), ctypes.sizeof(frame))
	return [frame.left, frame.top, frame.right, frame.bottom]


def load_positions():
	if POSITIONS_FILE.is_file():
		return json.loads(POSITIONS_FILE.read_text(encoding="utf-8"))
	return {}


def save_positions(name, apps):
	layouts = load_positions()
	windows = {}
	for app in apps:
		hwnd = app_window(POSITION_APPS[app])
		if hwnd is None:
			print("%s: no visible window; not saved" % app)
			continue
		windows[app] = {"exe": POSITION_APPS[app], "frame": hwnd_frame(hwnd)}
	layouts[name] = {"saved": time.strftime("%Y-%m-%d"), "workAreas": [list(area) for area in monitors()], "windows": windows}
	POSITIONS_FILE.write_text(format_json(layouts, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
	return layouts[name]


def restore_positions(name):
	layouts = load_positions()
	if name not in layouts:
		raise ValueError("no layout %r; saved: %s" % (name, ", ".join(sorted(layouts)) or "none"))
	# <!-- custom: A layout saved on other monitors could put a window off screen, so a changed set of work areas is reported rather than ignored. (Claude Code Opus 5.5) -->
	if layouts[name].get("workAreas") != [list(area) for area in monitors()]:
		print("warning: the monitors differ from when %r was saved" % name)
	result = {}
	for app, entry in sorted(layouts[name]["windows"].items()):
		hwnd = app_window(entry["exe"])
		if hwnd is None:
			result[app] = "no visible window"
			continue
		result[app] = place_window(hwnd, *entry["frame"])
	return result


def main():
	parser = argparse.ArgumentParser(description="Screenshot, click, type into or close a running Civ4 window or any other app's window by process ID.")
	sub = parser.add_subparsers(dest="command", required=True)
	sub.add_parser("list", help="list running Civ4 processes and their command lines")
	shot = sub.add_parser("screenshot", help="save a PNG of the window")
	shot.add_argument("--crop", type=int, nargs=4, metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"), help="keep only this window-relative rectangle")
	shot.add_argument("--layout", help="desktop usage layout from app_layouts.json, required with --crop-name")
	shot.add_argument("--crop-name", help="named crop from the selected desktop usage layout")
	shot.add_argument("--scale", type=float, default=1.0, help="shrink the result, e.g. 0.5; crops read far cheaper than full windows")
	shot.add_argument("--page", action="store_true", help="in Chrome, keep only the web page, without the tabs, address and bookmarks bars")
	clip = sub.add_parser("clipboard", help="save the image on the clipboard, such as the user's screen capture")
	clip.add_argument("--out", type=Path, required=True)
	clip.add_argument("--crop", type=int, nargs=4, metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"))
	clip.add_argument("--scale", type=float, default=1.0)
	shot.add_argument("--pid", type=int, required=True)
	shot.add_argument("--out", required=True)
	shot.add_argument("--method", choices=("window", "screen"), default="window", help="window: PrintWindow, works while covered; screen: bring to front and grab the screen area")
	press = sub.add_parser("click", help="click a window-relative point (physical pixels, as in screenshots), with the left button unless --button says otherwise")
	press.add_argument("--pid", type=int, required=True)
	press.add_argument("x", type=int, nargs="?")
	press.add_argument("y", type=int, nargs="?")
	press.add_argument("--point", help="a named Civ4 point or a desktop usage point with --layout")
	press.add_argument("--layout", help="desktop usage layout from app_layouts.json")
	press.add_argument("--with", dest="modifiers", action="append", choices=("ctrl", "shift", "alt"), default=[], help="hold this key during the click; repeat for several")
	press.add_argument("--double", action="store_true", help="double-click")
	press.add_argument("--button", choices=sorted(DRAG_BUTTONS), default="left", help="the mouse button, such as right for a Sevopedia link's right click")
	point = sub.add_parser("hover", help="move the pointer to a window-relative point without clicking or focusing, e.g. to show a tooltip")
	point.add_argument("--pid", type=int, required=True)
	point.add_argument("--front", action="store_true", help="bring the window forward first, through its title bar; Civ4's plot help needs it")
	point.add_argument("x", type=int, nargs="?")
	point.add_argument("y", type=int, nargs="?")
	point.add_argument("--point", help="a named Civ4 point or a desktop usage point with --layout")
	point.add_argument("--layout", help="desktop usage layout from app_layouts.json")
	wheel = sub.add_parser("scroll", help="turn the mouse wheel over a window-relative point; positive clicks scroll up, negative down")
	wheel.add_argument("--pid", type=int, required=True)
	wheel.add_argument("x", type=int, nargs="?")
	wheel.add_argument("y", type=int, nargs="?")
	wheel.add_argument("clicks", type=int, nargs="?")
	wheel.add_argument("--clicks", dest="mapped_clicks", type=int, help="wheel clicks when using a named point")
	wheel.add_argument("--layout", help="desktop layout from app_layouts.json")
	wheel.add_argument("--point", help="named scroll point in the selected desktop layout")
	pull = sub.add_parser("drag", help="press a mouse button at one window point, move to another and release, e.g. to turn a 3D view")
	pull.add_argument("--pid", type=int, required=True)
	for name in ("x1", "y1", "x2", "y2"):
		pull.add_argument(name, type=int)
	pull.add_argument("--button", choices=sorted(DRAG_BUTTONS), default="left")
	pull.add_argument("--steps", type=int, default=20, help="pointer moves between the two points")
	pull.add_argument("--with", dest="modifiers", action="append", choices=("ctrl", "shift", "alt"), default=[], help="hold this key during the drag; repeat for several")
	box = sub.add_parser("paste", help="click a window-relative point, such as a message box, and paste text without sending it")
	box.add_argument("--pid", type=int, required=True)
	box.add_argument("x", type=int)
	box.add_argument("y", type=int)
	source = box.add_mutually_exclusive_group(required=True)
	source.add_argument("--text")
	source.add_argument("--file", type=Path, help="UTF-8 file holding the text, which avoids shell quoting")
	box.add_argument("--send", choices=["enter", "ctrl+enter"], help="also press this key in the same focus grab, so the user's window is left for less time")
	press_key = sub.add_parser("key", help="bring the window to the front and press one key, e.g. enter to send a pasted message")
	press_key.add_argument("--pid", type=int, required=True)
	press_key.add_argument("name", help="a key or combination such as enter, f10, ctrl+left or ctrl+shift+x")
	press_key.add_argument("--count", type=int, default=1, help="press it this many times")
	press_key.add_argument("--hold", type=float, default=0.5, help="seconds to keep the window in front after the last press, so a game reads it")
	typing = sub.add_parser("type", help="bring the window to the front and type text as key presses, using the active keyboard layout")
	typing.add_argument("--pid", type=int, required=True)
	typing.add_argument("text")
	typing.add_argument("--us-keys", action="store_true", help="send ASCII as US-keyboard keys whatever the layout, for Civ4's Sevopedia search box, which reads key codes; Civ4's own text boxes, such as the autoplay turn box, need the default")
	dump = sub.add_parser("dump", help="at Civ4's crash prompt, press Full Dump (or --kind normal) by its label and wait until the .dmp file is written")
	dump.add_argument("--pid", type=int, required=True)
	dump.add_argument("--kind", choices=("full", "normal"), default="full")
	dump.add_argument("--timeout", type=float, default=300.0)
	button = sub.add_parser("button", help="press a button by its label in a window found by --pid or by --title prefix, such as Save (Enregistrer) in the Save As dialog of a browser-pane download")
	button.add_argument("label", help="the button's text without its & accelerator, in the system's language")
	button.add_argument("--pid", type=int)
	button.add_argument("--title", help="the window title's start, such as https://drive.usercontent.google.com/")
	button.add_argument("--timeout", type=float, default=10.0, help="seconds to wait for the button to appear")
	idle = sub.add_parser("wait-idle", help="wait until nobody has typed or moved the mouse for a while, e.g. before a browser-pane download, whose Save As dialog blocks the Claude app")
	idle.add_argument("--seconds", type=float, default=5.0)
	idle.add_argument("--timeout", type=float, default=600.0)
	saving = sub.add_parser("save-download", help="answer the Save As dialog of a browser-pane download in Downloads, never replacing a file: an existing name gets the time, \"name_20261123T091234.ext\"")
	saving.add_argument("--title", default="https://", help="the dialog title's start, the download's URL, such as https://drive.usercontent.google.com/")
	saving.add_argument("--timeout", type=float, default=15.0, help="seconds to wait for the dialog")
	saving.add_argument("--expect", help="the file name asked for, as the site shows it; any other name in the dialog stops it, as typing may have replaced it")
	saving.add_argument("--folder", type=Path, default=Path.home() / "Downloads", help="where to save (default: the user's Downloads)")
	close = sub.add_parser("close", help="send WM_CLOSE, as the title bar's X does, to one client or to every client running --mod")
	close.add_argument("--pid", type=int)
	close.add_argument("--mod", help="every Civ4 client whose command line names this mod, such as AdvCiv-SAS")
	close.add_argument("--wait", type=float, default=0.0, help="wait up to this many seconds for each to exit")
	close.add_argument("--force", action="store_true", help="end a client still running after --wait")
	keep = sub.add_parser("positions", help="save, restore or list named window layouts of the Claude app, the Codex app (ChatGPT.exe) and Civ4, found by program name; kept in layouts/window_positions.json")
	keep.add_argument("action", choices=("save", "restore", "list"))
	keep.add_argument("name", nargs="?", default="default", help="the layout's name (default 'default')")
	keep.add_argument("--apps", nargs="+", choices=sorted(POSITION_APPS), default=sorted(POSITION_APPS), help="save: which windows (default all three)")
	sub.add_parser("monitors", help="list each monitor's work area, the screen minus the taskbar, numbered from the left")
	place = sub.add_parser("move", help="place the window on one monitor's work area: the full area, or its left or right half")
	place.add_argument("--pid", type=int, required=True)
	place.add_argument("--monitor", type=int, default=1, help="1 is the leftmost monitor")
	place.add_argument("part", choices=("full", "maximize", "left", "right", "topleft", "bottomleft", "beside"), help="full, left or right half; maximize: a Windows maximize on that monitor, as the title bar's button does; topleft or bottomleft: that corner of the work area at the window's own size or --size; beside: the area right of --beside's window")
	place.add_argument("--size", type=int, nargs=2, metavar=("WIDTH", "HEIGHT"), help="topleft and bottomleft: the visible frame's size instead of the current one")
	place.add_argument("--beside", type=int, help="beside: the process whose window to fill the area right of")
	# <!-- custom: click, key, type and paste take the focus from whatever window the user is typing in, so their keystrokes then land in the target: on 2026-11-11 the user's typing turned Civ4's autoplay turn box into "ntwt".
	# So these wait, by default, until the user has been idle for a few seconds; the same rule agent_message.py follows. (Claude Code Opus 5.5) -->
	for focusing in (press, pull, box, press_key, typing, point, wheel):
		focusing.add_argument("--idle-seconds", type=float, default=3.0, help="first wait until nobody has typed or moved the mouse for this long; 0 skips the wait")
		focusing.add_argument("--idle-timeout", type=float, default=300.0, help="give up after this many seconds of waiting")
	args = parser.parse_args()
	if args.command == "drag" and args.steps < 1:
		parser.error("drag --steps must be positive")
	if args.command == "type" and args.us_keys and any(character not in US_KEYS for character in args.text):
		parser.error("--us-keys accepts only printable ASCII")
	# <!-- custom: Mapped desktop hovers and scrolls move the user's pointer too, so wait for idle just as for clicks. (GPT-6.1-Sol) -->
	waits_for_idle = args.command in ("click", "drag", "paste", "key", "type") or (args.command in ("hover", "scroll") and args.layout)
	if waits_for_idle and args.idle_seconds > 0 and not wait_for_idle_user(args.idle_seconds, args.idle_timeout):
		sys.exit("the user kept typing or moving the mouse for %d s; nothing was sent" % args.idle_timeout)

	if args.command == "list":
		for pid, cmd in civ4_processes():
			print("%d\t%s" % (pid, cmd))
	elif args.command == "screenshot":
		if bool(args.crop_name) != bool(args.layout) or (args.crop_name and args.crop):
			parser.error("use --layout and --crop-name together, or pass --crop")
		crop = usage_geometry(args.pid, args.crop_name, args.layout, "crops") if args.crop_name else args.crop
		path, box = screenshot(args.pid, args.out, args.method, crop, args.scale, args.page)
		print("saved %s window=%s" % (path, box))
	elif args.command == "clipboard":
		path, size = save_clipboard_image(args.out, args.crop, args.scale)
		print("saved %s size=%dx%d" % ((path,) + size))
	elif args.command in ("click", "hover"):
		if args.layout:
			if not args.point or args.x is not None or args.y is not None:
				parser.error("--layout needs --point NAME instead of x and y")
			args.x, args.y = usage_geometry(args.pid, args.point, args.layout, "points")
		elif args.point:
			args.x, args.y = named_point(args.pid, args.point)
		elif args.x is None or args.y is None:
			sys.exit("%s needs x and y, or --point NAME" % args.command)
		if args.command == "click":
			print("clicked screen point %d,%d" % click(args.pid, args.x, args.y, tuple(MODIFIER_VKS[m] for m in args.modifiers), args.double, give_back=True, button=args.button))
		else:
			print("pointer at screen point %d,%d" % hover(args.pid, args.x, args.y, args.front))
	elif args.command == "drag":
		start, end = drag(args.pid, args.x1, args.y1, args.x2, args.y2, args.button, args.steps, tuple(MODIFIER_VKS[m] for m in args.modifiers))
		print("dragged %s from %d,%d to %d,%d" % ((args.button,) + start + end))
	elif args.command == "scroll":
		if args.layout or args.point or args.mapped_clicks is not None:
			if not args.layout or not args.point or args.mapped_clicks is None or args.x is not None:
				parser.error("mapped scroll needs --layout, --point and --clicks instead of x y clicks")
			args.x, args.y = usage_geometry(args.pid, args.point, args.layout, "points")
			args.clicks = args.mapped_clicks
		elif args.clicks is None:
			parser.error("scroll needs x y clicks")
		scroll(args.pid, args.x, args.y, args.clicks)
		print("scrolled %d at %d,%d" % (args.clicks, args.x, args.y))
	elif args.command == "paste":
		text = args.text if args.text is not None else args.file.read_text(encoding="utf-8")
		print("pasted %d characters at screen point %d,%d" % ((len(text),) + paste(args.pid, args.x, args.y, text, args.send)))
	elif args.command == "key":
		key(args.pid, args.name, args.hold, args.count)
		print("pressed %s %d time(s)" % (args.name, args.count))
	elif args.command == "type":
		type_text(args.pid, args.text, us_keys=args.us_keys)
		print("typed %d characters" % len(args.text))
	elif args.command == "dump":
		(path, size) = save_dump(args.pid, args.kind, args.timeout)
		print("dump written: %s (%d bytes); move it beside its DLL and PDB before another crash replaces it" % (path, size))
	elif args.command == "close":
		if (args.pid is None) == (args.mod is None):
			sys.exit("close needs exactly one of --pid or --mod")
		close_clients(args.pid, args.mod, args.wait, args.force)
	elif args.command == "button":
		if (args.pid is None) == (args.title is None):
			sys.exit("button needs exactly one of --pid or --title")
		# <!-- custom: Waits, as a dialog can open a moment after the click that asks for it; BM_CLICK, as in save_dump, needs no focus, so it does not take the user's keyboard. (Claude code Opus 5.5) -->
		deadline = time.monotonic() + args.timeout
		found = find_button(args.pid, args.label, args.title)
		while found is None and time.monotonic() < deadline:
			time.sleep(0.5)
			found = find_button(args.pid, args.label, args.title)
		if found is None:
			sys.exit("no %r button in a window %s" % (args.label, "of process %d" % args.pid if args.pid is not None else "titled %r..." % args.title))
		dialog = USER32.GetAncestor(found, 2)
		owner = wt.DWORD()
		USER32.GetWindowThreadProcessId(dialog, ctypes.byref(owner))
		if not USER32.PostMessageW(found, 0x00F5, 0, 0):
			sys.exit("could not send the click to %r: Windows error %d" % (args.label, ctypes.GetLastError()))
		# <!-- custom: A press is not a result: Save stops at Windows' prompt to replace the file when the name already exists, the user asked (2026-11-23), so the dialog must close, and a prompt in its place is left to the user rather than answered.
		# Closed means the window no longer exists: behind such a prompt the Save dialog is only hidden, which this first took for closed (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		deadline = time.monotonic() + 5.0
		while USER32.IsWindow(dialog) and time.monotonic() < deadline:
			time.sleep(0.25)
		if USER32.IsWindow(dialog):
			titles = []
			proc_type = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

			def collect(hwnd, _lparam):
				pid = wt.DWORD()
				USER32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
				if pid.value == owner.value and USER32.IsWindowVisible(hwnd) and window_title(hwnd):
					titles.append(window_title(hwnd))
				return True

			USER32.EnumWindows(proc_type(collect), 0)
			sys.exit("pressed %r, but its window is still open, perhaps behind a prompt; left for the user: %s" % (args.label, " | ".join(titles)))
		print("pressed %r; its window closed" % args.label)
	elif args.command == "wait-idle":
		# <!-- custom: A download's Save As dialog popped up while the user was typing in the Claude app and took the app until answered (2026-11-23), so the click that starts a download waits for this first. (Claude code Opus 5.5) -->
		if not wait_for_idle_user(args.seconds, args.timeout):
			sys.exit("the user was not idle for %s seconds within %s seconds" % (args.seconds, args.timeout))
		print("idle for %s seconds" % args.seconds)
	elif args.command == "save-download":
		print("saved as %s" % save_download(args.title, args.timeout, args.expect, args.folder))
	elif args.command == "monitors":
		for number, area in enumerate(monitors(), 1):
			print("%d\twork area %d,%d to %d,%d (%dx%d)" % ((number,) + area + (area[2] - area[0], area[3] - area[1])))
	elif args.command == "positions":
		if args.action == "save":
			print(format_json(save_positions(args.name, args.apps), indent=1))
		elif args.action == "restore":
			print(format_json(restore_positions(args.name), indent=1))
		else:
			print(format_json(load_positions(), indent=1, sort_keys=True))
	elif args.command == "move":
		# <!-- custom: The user asked that the tools never shrink a window to unreadable, after a SASPilot console was squeezed into a sliver (2026-11-20); refuse a size below 640 x 400 rather than place it.
		# Growing a window, such as a 1920 x 1080 Civ4 to fill a 4K monitor, is useful: on 2026-11-20 the user's 4K view showed the few px left between advisors and the scoreboard, which took the scoreboard's width from 395 to 393, and windows close to the 4K screen's size measured how the main-menu setup screens scale for the EXE patch of KI#1082 (2026-11-12).
		# But shrinking a running Civ4 only stretches its picture: a 1920 x 1080 test that way showed blurry text and advisors not laid out for 1920.
		# To test a smaller screen, start Civ4 at that resolution instead (the INI's ScreenWidth and ScreenHeight); a 2005 game supports low resolutions natively. (Claude Code Opus 5.5) -->
		if args.size and (args.size[0] < 640 or args.size[1] < 400):
			sys.exit("refusing --size %d x %d: below 640 x 400 a window is unreadable" % tuple(args.size))
		print("window now at %s" % (move(args.pid, args.monitor, args.part, args.size, args.beside),))


if __name__ == "__main__":
	main()

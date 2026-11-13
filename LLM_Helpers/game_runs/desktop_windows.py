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
# <!-- custom: subprocess runs PowerShell for WMI; sys, time and pathlib handle exit codes, waits and paths. (Claude Code Opus 5.5) -->
import os
import shutil
import struct
import subprocess
import sys
import time
from pathlib import Path

USER32 = ctypes.windll.user32
WM_CLOSE = 0x0010
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


def screenshot(pid, out_path, method="window", crop=None, scale=1.0):
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
	# <!-- custom: crop is (left, top, right, bottom) in window pixels and scale shrinks the result: a full 3840-pixel window cost many tokens per read, so on 2026-11-10 nearly every screenshot was cropped and shrunk with throwaway Pillow code; these two options replace it. (Claude Code Opus 5.5) -->
	if crop:
		image = image.crop(tuple(crop))
	if scale != 1.0:
		image = image.resize((max(1, int(image.width * scale)), max(1, int(image.height * scale))))
	out_path = Path(out_path)
	out_path.parent.mkdir(parents=True, exist_ok=True)
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


def window_pid(hwnd):
	owner = wt.DWORD()
	USER32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
	return owner.value


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


def click(pid, x, y, modifiers=(), double=False):
	# <!-- custom: The caller can request a chord or double click so both forms use the same bounds and ownership checks. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
	# <!-- custom: Codex's 2026-11-10 review found that click pressed the mouse even when the window had not come to the front or the point lay outside it, so the click could land in whatever window was there, such as the user's. Check the bounds, the foreground window and the window under the point before pressing; a Civ4 popup is a separate window of the same process, so the last check compares processes, not handles. (Claude Code Opus 5.5) -->
	hwnd, screen_x, screen_y = window_point(pid, x, y)
	foreground = bring_to_front(hwnd, pid)
	if window_pid(foreground) != pid:
		raise RuntimeError("process %d's window did not come to the front; the foreground window belongs to process %d" % (pid, window_pid(foreground)))
	under = USER32.WindowFromPoint(wt.POINT(screen_x, screen_y))
	if not under or window_pid(under) != pid:
		raise RuntimeError("screen point %d,%d is covered by a window of process %d" % (screen_x, screen_y, window_pid(under) if under else 0))
	USER32.SetCursorPos(screen_x, screen_y)
	time.sleep(0.05)
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
			USER32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
			button_down = True
			time.sleep(0.05)
			USER32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
			button_down = False
			time.sleep(0.05)
	finally:
		if button_down:
			USER32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
		for modifier in reversed(pressed):
			key_event(modifier, up=True)
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


def hover(pid, x, y):
	# <!-- custom: Move the pointer without clicking or focusing, to reveal tooltips such as Codex's usage reset times.
	# A click into the Claude app while the user typed there would have taken focus from their typing; a hover takes none. (Claude Code Opus 5.5) -->
	_hwnd, screen_x, screen_y = window_point(pid, x, y)
	USER32.SetCursorPos(screen_x, screen_y)
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
	"left": (0x25, ()), "up": (0x26, ()), "right": (0x27, ()), "down": (0x28, ()), "pgup": (0x21, ()), "pgdn": (0x22, ()), "home": (0x24, ()), "end": (0x23, ())}
KEYEVENTF_EXTENDEDKEY = 0x0001
# <!-- custom: Arrow, page, home, end, insert and delete keys sit on the extended keyboard, so their events need KEYEVENTF_EXTENDEDKEY, or a program reading scan codes sees the number pad's keys instead. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
EXTENDED_KEYS = {0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x2D, 0x2E}


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
		tap(ord("V"), (VK_CONTROL,))
		time.sleep(0.3)
		if send:
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
		raise ValueError("unknown key %r" % name)
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


def find_button(pid, label):
	# <!-- custom: The button of that label in any top-level window of pid, such as the crash prompt's "Full Dump", or None. (Claude code Opus 5.5) -->
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
		if owner.value == pid:
			USER32.EnumChildWindows(hwnd, proc_type(child), 0)
		return True

	USER32.EnumWindows(proc_type(top), 0)
	return found[0] if found else None


def minidump_pid(path):
	# <!-- custom: The process ID a minidump records in its MiscInfo stream (type 15; ProcessId at offset 8 when Flags1 has bit 1), or None. 'dump' checks it, as every Civ4 writes the same file name (Codex's review). See KI#1089. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
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
	# <!-- custom: At KI#1088's crash prompt (2026-11-13) a full dump took three tries: clicking by window coordinates, then two wait loops that started PowerShell on each pass and showed nothing for minutes. This presses the button by its label with BM_CLICK, which needs no focus or coordinates, then waits for the file to be finished, about a dozen seconds for 1.38 GB.
	# BM_CLICK can fail on an inactive dialog (Microsoft's documentation, as Codex noted); the timeout then reports no dump rather than a stale one. Not yet tried on a real prompt.
	# A full dump is the user's rule (README_DLL_Compilation.md): a normal one lacks the heap. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	button = find_button(pid, DUMP_BUTTONS[kind])
	if button is None:
		raise SystemExit("no %r button in process %d's windows; is the crash prompt up?" % (DUMP_BUTTONS[kind], pid))
	# <!-- custom: Codex's review: the first version accepted a file from just before the press and took two equal sizes for the end, which a pause in writing also gives. Now the file must differ from its state before the press, and it is done once it can be opened without sharing writes, which fails while the writer still holds it. The name is shared by every Civ4, so a second client's crash would replace it. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
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


def process_alive(pid):
	handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)  # <!-- custom: PROCESS_QUERY_LIMITED_INFORMATION (Claude Code Opus 5.5) -->
	if not handle:
		return False
	code = wt.DWORD()
	ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
	ctypes.windll.kernel32.CloseHandle(handle)
	return code.value == 259  # <!-- custom: STILL_ACTIVE (Claude Code Opus 5.5) -->


def civ4_processes():
	# <!-- custom: Return [(pid, command line)] for every running Civ4 client. (Claude Code Opus 5.5) -->
	command = "Get-CimInstance Win32_Process -Filter \"Name='%s'\" | ForEach-Object { \"$($_.ProcessId)`t$($_.CommandLine)\" }" % EXE_NAME
	output = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True, text=True, check=True).stdout
	result = []
	for line in output.splitlines():
		if "\t" in line:
			pid, cmd = line.split("\t", 1)
			result.append((int(pid), cmd))
	return result


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
	import json
	path = Path(__file__).resolve().parent / "ui_maps" / "app_layouts.json"
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
	# <!-- custom: json reads the points file; imported here since only named points need it. (Claude Code Opus 5.5) -->
	import json
	make_dpi_aware()
	hwnd = find_window(pid)
	if hwnd is None:
		sys.exit("no window for process %d" % pid)
	left, top, right, bottom = window_rect(hwnd)
	size = (right - left, bottom - top)
	if "." in name:
		# <!-- custom: SCREEN.CONTROL names come from civ4_ui_map.json, the map of Civ4's screens outside a game, such as single_player.load_game. (Claude Code Opus 5.5) -->
		ui = json.loads((Path(__file__).resolve().parent / "ui_maps" / "civ4_ui_map.json").read_text(encoding="utf-8"))
		if abs(size[0] - ui["window"][0]) > 20 or abs(size[1] - ui["window"][1]) > 20:
			sys.exit("civ4_ui_map.json was measured on a %dx%d window, not %dx%d" % (ui["window"][0], ui["window"][1], size[0], size[1]))
		screen_name, control = name.split(".", 1)
		screen = ui["screens"].get(screen_name)
		if screen is None or control not in screen["controls"]:
			sys.exit("no control %r in civ4_ui_map.json" % name)
		return tuple(screen["controls"][control]["xy"])
	data = json.loads((Path(__file__).resolve().parent / "ui_maps" / "civ4_points.json").read_text(encoding="utf-8"))
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


def move(pid, monitor, part):
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
	target = {"full": (left, right), "left": (left, middle), "right": (middle, right)}[part]
	USER32.ShowWindow(hwnd, 9)
	frame = wt.RECT()
	ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, 9, ctypes.byref(frame), ctypes.sizeof(frame))
	outer = window_rect(hwnd)
	border_left, border_top = frame.left - outer[0], frame.top - outer[1]
	border_right, border_bottom = outer[2] - frame.right, outer[3] - frame.bottom
	x = target[0] - border_left
	y = top - border_top
	width = target[1] - target[0] + border_left + border_right
	height = bottom - top + border_top + border_bottom
	# <!-- custom: 0x0014 is SWP_NOZORDER | SWP_NOACTIVATE, so the move neither raises the window nor takes focus from the user. (Claude Code Opus 5.5) -->
	USER32.SetWindowPos(hwnd, None, x, y, width, height, 0x0014)
	return window_rect(hwnd)


def main():
	parser = argparse.ArgumentParser(description="Screenshot, click, type into or close a running Civ4 window or any other app's window by process ID.")
	sub = parser.add_subparsers(dest="command", required=True)
	sub.add_parser("list", help="list running Civ4 processes and their command lines")
	shot = sub.add_parser("screenshot", help="save a PNG of the window")
	shot.add_argument("--crop", type=int, nargs=4, metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"), help="keep only this window-relative rectangle")
	shot.add_argument("--layout", help="desktop usage layout from app_layouts.json, required with --crop-name")
	shot.add_argument("--crop-name", help="named crop from the selected desktop usage layout")
	shot.add_argument("--scale", type=float, default=1.0, help="shrink the result, e.g. 0.5; crops read far cheaper than full windows")
	clip = sub.add_parser("clipboard", help="save the image on the clipboard, such as the user's screen capture")
	clip.add_argument("--out", type=Path, required=True)
	clip.add_argument("--crop", type=int, nargs=4, metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"))
	clip.add_argument("--scale", type=float, default=1.0)
	shot.add_argument("--pid", type=int, required=True)
	shot.add_argument("--out", required=True)
	shot.add_argument("--method", choices=("window", "screen"), default="window", help="window: PrintWindow, works while covered; screen: bring to front and grab the screen area")
	press = sub.add_parser("click", help="left-click a window-relative point (physical pixels, as in screenshots)")
	press.add_argument("--pid", type=int, required=True)
	press.add_argument("x", type=int, nargs="?")
	press.add_argument("y", type=int, nargs="?")
	press.add_argument("--point", help="a named Civ4 point or a desktop usage point with --layout")
	press.add_argument("--layout", help="desktop usage layout from app_layouts.json")
	press.add_argument("--with", dest="modifiers", action="append", choices=("ctrl", "shift", "alt"), default=[], help="hold this key during the click; repeat for several")
	press.add_argument("--double", action="store_true", help="double-click")
	point = sub.add_parser("hover", help="move the pointer to a window-relative point without clicking or focusing, e.g. to show a tooltip")
	point.add_argument("--pid", type=int, required=True)
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
	close = sub.add_parser("close", help="send WM_CLOSE, as the title bar's X does")
	close.add_argument("--pid", type=int, required=True)
	dump = sub.add_parser("dump", help="at Civ4's crash prompt, press Full Dump (or --kind normal) by its label and wait until the .dmp file is written")
	dump.add_argument("--pid", type=int, required=True)
	dump.add_argument("--kind", choices=("full", "normal"), default="full")
	dump.add_argument("--timeout", type=float, default=300.0)
	sub.add_parser("monitors", help="list each monitor's work area, the screen minus the taskbar, numbered from the left")
	place = sub.add_parser("move", help="place the window on one monitor's work area: the full area, or its left or right half")
	place.add_argument("--pid", type=int, required=True)
	place.add_argument("--monitor", type=int, default=1, help="1 is the leftmost monitor")
	place.add_argument("part", choices=("full", "left", "right"))
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
		path, box = screenshot(args.pid, args.out, args.method, crop, args.scale)
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
			print("clicked screen point %d,%d" % click(args.pid, args.x, args.y, tuple(MODIFIER_VKS[m] for m in args.modifiers), args.double))
		else:
			print("pointer at screen point %d,%d" % hover(args.pid, args.x, args.y))
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
	elif args.command == "close":
		if not request_close(args.pid):
			sys.exit("no window for process %d" % args.pid)
		print("WM_CLOSE sent to %d" % args.pid)
	elif args.command == "dump":
		(path, size) = save_dump(args.pid, args.kind, args.timeout)
		print("dump written: %s (%d bytes); move it beside its DLL and PDB before another crash replaces it" % (path, size))
	elif args.command == "monitors":
		for number, area in enumerate(monitors(), 1):
			print("%d\twork area %d,%d to %d,%d (%dx%d)" % ((number,) + area + (area[2] - area[0], area[3] - area[1])))
	elif args.command == "move":
		print("window now at %s" % (move(args.pid, args.monitor, args.part),))


if __name__ == "__main__":
	main()

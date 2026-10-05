"""The few Win32 calls the Windows targets need, through ctypes (stdlib)."""
import ctypes
import os
import sys
from pathlib import Path

HWND_BROADCAST = 0xFFFF
WM_FONTCHANGE = 0x001D
WM_SETTINGCHANGE = 0x001A
SMTO_ABORTIFHUNG = 0x0002
TIMEOUT_MS = 2000


def _user32():
    return ctypes.WinDLL("user32", use_last_error=True)


def _gdi32():
    return ctypes.WinDLL("gdi32", use_last_error=True)


def _broadcast(msg, lparam):
    user32 = _user32()
    send = user32.SendMessageTimeoutW
    send.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_void_p,
                     ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_size_t)]
    result = ctypes.c_size_t()
    send(HWND_BROADCAST, msg, 0, lparam, SMTO_ABORTIFHUNG, TIMEOUT_MS, ctypes.byref(result))


def setting_change(area):
    """WM_SETTINGCHANGE with lParam = area (e.g. "ImmersiveColorSet")."""
    if sys.platform != "win32":
        return
    _broadcast(WM_SETTINGCHANGE, ctypes.cast(ctypes.c_wchar_p(area), ctypes.c_void_p))


def font_change():
    if sys.platform != "win32":
        return
    _broadcast(WM_FONTCHANGE, None)


def add_font(path):
    """Load a font file into the current session (what a logon does for HKCU\\...\\Fonts)."""
    if sys.platform != "win32":
        return 0
    return _gdi32().AddFontResourceW(ctypes.c_wchar_p(str(path)))


def remove_font(path):
    """Unload a font file from the session, so the file can be deleted. Repeats until the
    session's reference count reaches zero (each AddFontResource adds one)."""
    if sys.platform != "win32":
        return
    gdi32 = _gdi32()
    for _ in range(16):
        if not gdi32.RemoveFontResourceW(ctypes.c_wchar_p(str(path))):
            break


# Windows Terminal reads fragments only when it (re)loads its settings, and every new window
# or tab reuses the running process. It reloads when settings.json changes on disk, so bumping
# the file's modification time (content untouched) makes a running terminal pick up the
# fragment, or drop it on uninstall.
TERMINAL_SETTINGS = (
    "Packages/Microsoft.WindowsTerminal_8wekyb3d8bbwe/LocalState/settings.json",
    "Packages/Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe/LocalState/settings.json",
    "Microsoft/Windows Terminal/settings.json",
)


def reload_terminal():
    base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData/Local")
    for rel in TERMINAL_SETTINGS:
        path = base / rel
        if path.is_file():
            os.utime(path, None)


def notify(area):
    """Tell running programs that something changed: [[post]] notify = "<area>".

    "fonts" -> WM_FONTCHANGE; "windows-terminal" -> reload_terminal(); anything else is the
    lParam of a WM_SETTINGCHANGE broadcast (e.g. "ImmersiveColorSet").
    """
    if sys.platform != "win32":
        return
    if area == "fonts":
        font_change()
    elif area == "windows-terminal":
        reload_terminal()
    else:
        setting_change(area)

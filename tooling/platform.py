"""OS detection and per-platform view of targets (PHASE-WindowsOnly.md §3).

target.toml gains `platforms = ["linux"] | ["windows"] | both` (default: linux only, so the
existing targets keep working untouched). A target may also carry a `[windows]` table whose
keys replace the top-level ones when running on Windows (e.g. `brave` keeps its Linux `dest`
and adds a Windows one). On Linux nothing here changes behavior.
"""
import os
import sys
from pathlib import Path

LINUX = "linux"
WINDOWS = "windows"
KNOWN = (LINUX, WINDOWS)
DEFAULT_PLATFORMS = (LINUX,)


def current():
    return WINDOWS if sys.platform == "win32" else LINUX


def is_windows():
    return current() == WINDOWS


def windows_build():
    """(build, ubr) of the running Windows, e.g. (26300, 9457); None elsewhere."""
    if not is_windows():
        return None
    import winreg
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
        build = int(winreg.QueryValueEx(key, "CurrentBuildNumber")[0])
        try:
            ubr = int(winreg.QueryValueEx(key, "UBR")[0])
        except OSError:
            ubr = 0
    return build, ubr


def describe():
    if not is_windows():
        return "Linux"
    build, ubr = windows_build()
    return f"Windows build {build}.{ubr}"


def platforms_of(meta):
    platforms = meta.get("platforms", DEFAULT_PLATFORMS)
    if isinstance(platforms, str):
        platforms = [platforms]
    unknown = [p for p in platforms if p not in KNOWN]
    if unknown:
        raise ValueError(f"plataforma desconhecida: {', '.join(unknown)}")
    return tuple(platforms)


def supports(meta, platform=None):
    return (platform or current()) in platforms_of(meta)


def overlay(meta, platform=None):
    """meta with the `[<platform>]` table applied on top and every platform table removed.

    `detect_paths` in the overlay also drops an inherited `detect` (a POSIX shell command
    makes no sense on Windows).
    """
    platform = platform or current()
    out = {k: v for k, v in meta.items() if k not in KNOWN}
    extra = meta.get(platform)
    if isinstance(extra, dict):
        if "detect_paths" in extra and "detect" not in extra:
            out.pop("detect", None)
        out.update(extra)
    return out


def expand(path):
    """User path from a target.toml: `~` everywhere, `%VAR%` only on Windows."""
    if is_windows():
        path = os.path.expandvars(path)
    return os.path.expanduser(path)


def local_appdata():
    return Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData/Local")


def state_dir(theme_id):
    """Backups and render hashes: ~/.local/state/<id> on Linux, %LOCALAPPDATA%\\<id>\\state on Windows."""
    if is_windows():
        return local_appdata() / theme_id / "state"
    base = os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state"
    return Path(base) / theme_id


def tokens(theme_id):
    """Extra placeholders for target.toml/templates on this platform. Empty on Linux."""
    if not is_windows():
        return {}
    home = Path.home()
    yasb = os.environ.get("YASB_CONFIG_HOME") or str(home / ".config" / "yasb")
    return {
        "user_data": str(local_appdata() / theme_id),
        "local_appdata": str(local_appdata()),
        "yasb_config": yasb,
    }

"""Windhawk mod settings (W2, docs/SPIKE-S1.md).

Windhawk keeps each mod's settings in HKLM\\SOFTWARE\\Windhawk\\Engine\\Mods\\<mod>\\Settings,
writable only by administrators. W2 has no admin, so the tooling never writes there: it
generates the settings as YAML for Windhawk's "Textual mode" (the user pastes it once) and
only READS the registry to:
  - tell whether the mod is installed and whether it already has the generated settings;
  - export the current settings to the backup, so they can be pasted back.

The registry stores settings flattened: "controlStyles[0].styles[1]" = "...", numbers as
DWORD. GIBI_WINDHAWK_ROOT (tests only) points the reads at another key.
"""
import os
import re

try:
    import winreg
except ImportError:  # Linux: the backend is never called there
    winreg = None

DEFAULT_ROOT = r"HKLM\SOFTWARE\Windhawk"
ROOT_ENV = "GIBI_WINDHAWK_ROOT"
HIVES = {"HKLM": "HKEY_LOCAL_MACHINE", "HKCU": "HKEY_CURRENT_USER"}
_PART = re.compile(r"([^.\[\]]+)|\[(\d+)\]")


class WindhawkError(Exception):
    pass


def _root():
    root = os.environ.get(ROOT_ENV) or DEFAULT_ROOT
    hive, _, sub = root.partition("\\")
    if hive.upper() not in HIVES:
        raise WindhawkError(f"raiz do Windhawk inválida: {root}")
    return getattr(winreg, HIVES[hive.upper()]), sub


def _open(*parts):
    hive, sub = _root()
    return winreg.OpenKey(hive, "\\".join((sub, "Engine", "Mods", *parts)))


def installed(mod):
    try:
        _open(mod).Close()
        return True
    except FileNotFoundError:
        return False


def current(mod):
    """Flattened settings of an installed mod ({} if it has none)."""
    out = {}
    try:
        key = _open(mod, "Settings")
    except FileNotFoundError:
        return out
    with key:
        i = 0
        while True:
            try:
                name, value, _ = winreg.EnumValue(key, i)
            except OSError:
                break
            out[name] = value
            i += 1
    return out


# --- structure <-> flattened ---------------------------------------------------------------

def flatten(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(flatten(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = int(obj) if isinstance(obj, bool) else obj
    return out


def unflatten(flat):
    """Inverse of flatten() for the registry layout (lists come back in index order)."""
    root = {}
    for name, value in flat.items():
        parts = [(m.group(1), m.group(2)) for m in _PART.finditer(name)]
        node = root
        for n, (key, index) in enumerate(parts):
            last = n == len(parts) - 1
            nxt = parts[n + 1] if not last else None
            empty = [] if nxt and nxt[1] is not None else {}
            if index is None:
                if last:
                    node[key] = value
                else:
                    node = node.setdefault(key, empty)
            else:
                i = int(index)
                while len(node) <= i:
                    node.append(None)
                if last:
                    node[i] = value
                else:
                    if node[i] is None:
                        node[i] = empty
                    node = node[i]
    return root


def applied(desired, flat_current):
    """True if the mod's settings match `desired`, ignoring empty strings on both sides
    (Windhawk keeps [""] for an empty list)."""
    def meaningful(flat):
        return {k: v for k, v in flat.items() if v != ""}
    return meaningful(flatten(desired)) == meaningful(flat_current)


# --- YAML for Windhawk's "Textual mode" ----------------------------------------------------

def _scalar(value):
    # Windhawk stores on/off settings as numbers and rejects YAML booleans
    # ("Type mismatch ... expected number, but got boolean").
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int):
        return str(value)
    if value is None:
        return "''"
    return "'" + str(value).replace("'", "''") + "'"


def _yaml_lines(obj, indent):
    pad = " " * indent
    lines = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{pad}{k}:")
                lines += _yaml_lines(v, indent + 2)
            elif isinstance(v, (dict, list)):
                lines.append(f"{pad}{k}: {'[]' if isinstance(v, list) else '{}'}")
            else:
                lines.append(f"{pad}{k}: {_scalar(v)}")
    else:
        for item in obj:
            if isinstance(item, dict) and item:
                sub = _yaml_lines(item, indent + 2)
                lines.append(f"{pad}- {sub[0].lstrip()}")
                lines += sub[1:]
            elif isinstance(item, list) and item:
                sub = _yaml_lines(item, indent + 2)
                lines.append(f"{pad}- {sub[0].lstrip()}")
                lines += sub[1:]
            else:
                lines.append(f"{pad}- {_scalar(item)}")
    return lines


def to_yaml(settings, header=()):
    """Block-style YAML with every string single-quoted (XAML values are full of : < # " {)."""
    lines = [f"# {h}" for h in header] + _yaml_lines(settings, 0)
    return "\n".join(lines) + "\n"

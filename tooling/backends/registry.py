"""Registry backend (winreg): the Windows counterpart of kwriteconfig6 (PHASE-WindowsOnly.md §2).

Only HKEY_CURRENT_USER is accepted, which keeps W1/W2 free of admin rights.

Values travel through manifest.json as {"type": ..., "data": ...}:
  dword/qword -> int, string/expand_string -> str, binary -> hex string.
`None` means "the value did not exist" (restore deletes it).

GIBI_REGISTRY_REDIRECT (tests only): when set, every key is moved under
HKCU\\<redirect>\\..., so the selftest never touches the real keys.
"""
import os

from ..palette import hex_to_rgb, _mix

try:
    import winreg
except ImportError:  # Linux: the backend is never called there
    winreg = None

HIVES = {"HKCU": "HKEY_CURRENT_USER", "HKEY_CURRENT_USER": "HKEY_CURRENT_USER"}
TYPES = {
    "dword": "REG_DWORD",
    "qword": "REG_QWORD",
    "string": "REG_SZ",
    "expand_string": "REG_EXPAND_SZ",
    "binary": "REG_BINARY",
}
REDIRECT_ENV = "GIBI_REGISTRY_REDIRECT"


class RegistryError(Exception):
    pass


def split(key):
    """'HKCU\\Software\\X' -> 'Software\\X' (after the test redirect). Only HKCU is allowed."""
    hive, _, sub = key.replace("/", "\\").partition("\\")
    if hive.upper() not in HIVES:
        raise RegistryError(f"só HKCU é permitido (sem admin): {key}")
    sub = sub.strip("\\")
    if not sub:
        raise RegistryError(f"chave vazia: {key}")
    redirect = os.environ.get(REDIRECT_ENV)
    if redirect:
        sub = redirect.strip("\\") + "\\" + sub
    return sub


def display(sub):
    return "HKCU\\" + sub


def _type_name(reg_type):
    for name, const in TYPES.items():
        if getattr(winreg, const) == reg_type:
            return name
    raise RegistryError(f"tipo de registro não suportado: {reg_type}")


def _to_json(name, data):
    if name == "binary":
        return bytes(data or b"").hex()
    return data


def _from_json(name, data):
    if name == "binary":
        return bytes.fromhex(data)
    if name in ("dword", "qword"):
        return int(data)
    return str(data)


def read(sub, name):
    """{"type", "data"} of the value, or None if the key or value does not exist."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub) as key:
            data, reg_type = winreg.QueryValueEx(key, name)
    except FileNotFoundError:
        return None
    type_name = _type_name(reg_type)
    return {"type": type_name, "data": _to_json(type_name, data)}


def key_exists(sub):
    try:
        winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub).Close()
        return True
    except FileNotFoundError:
        return False


def missing_keys(sub):
    """Keys that writing to `sub` would create, deepest first (for restore cleanup)."""
    missing = []
    parts = sub.split("\\")
    for i in range(len(parts), 0, -1):
        path = "\\".join(parts[:i])
        if key_exists(path):
            break
        missing.append(path)
    return missing


def write(sub, name, value):
    type_name = value["type"]
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, sub, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, name, 0, getattr(winreg, TYPES[type_name]), _from_json(type_name, value["data"]))


def delete(sub, name):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, name)
    except FileNotFoundError:
        pass


def restore(sub, name, old):
    if old is None:
        delete(sub, name)
    else:
        write(sub, name, old)


def remove_empty_keys(paths):
    """Delete keys we created, if they ended up with no values and no subkeys."""
    for path in paths:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
                subkeys, values, _ = winreg.QueryInfoKey(key)
            if not subkeys and not values:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, path)
        except FileNotFoundError:
            continue


# --- value conversion from target.toml ---------------------------------------------------

def _dword(value):
    return int(value) & 0xFFFFFFFF


def _abgr(hex_color, alpha=255):
    r, g, b = hex_to_rgb(hex_color)
    return (alpha << 24) | (b << 16) | (g << 8) | r


def _argb(hex_color, alpha=255):
    r, g, b = hex_to_rgb(hex_color)
    return (alpha << 24) | (r << 16) | (g << 8) | b


def accent_shades(hex_color):
    """Light3..Light1, accent, Dark1..Dark3 for an accent color (docs/SPIKE-S0.md §2).

    Windows' own algorithm is undocumented (it also shifts the hue); a plain mix with white
    and black is close enough and keeps every shade derived from the palette.
    """
    light = [_mix(hex_color, "#FFFFFF", t) for t in (0.45, 0.30, 0.15)]
    dark = [_mix(hex_color, "#000000", t) for t in (0.15, 0.40, 0.65)]
    return light + [hex_color.upper()] + dark


def accent_palette(hex_color):
    """AccentPalette: 8 colors as R G B 00. The 8th slot (unused by the shell) repeats Dark3."""
    shades = accent_shades(hex_color)
    out = bytearray()
    for color in shades + shades[-1:]:
        out += bytes(hex_to_rgb(color)) + b"\x00"
    return bytes(out)


def desired(spec, rendered):
    """{"type", "data"} wanted by a [[registry]] entry. `rendered` is its value after the render.

    format = "abgr" | "argb" (color -> DWORD, optional `alpha` 0-255), "accent-palette"
    (color -> 32-byte binary), "shade:N" (color -> ABGR DWORD of AccentPalette slot N).
    """
    type_name = spec.get("type", "string")
    if type_name not in TYPES:
        raise RegistryError(f"tipo desconhecido: {type_name}")
    fmt = spec.get("format")
    alpha = int(spec.get("alpha", 255))
    if fmt == "abgr":
        data = _abgr(rendered, alpha)
    elif fmt == "argb":
        data = _argb(rendered, alpha)
    elif fmt == "accent-palette":
        data = accent_palette(rendered)
    elif fmt and fmt.startswith("shade:"):
        data = _abgr(accent_shades(rendered)[int(fmt.split(":", 1)[1])], alpha)
    elif fmt:
        raise RegistryError(f"format desconhecido: {fmt}")
    elif type_name in ("dword", "qword"):
        data = int(rendered, 0)
    elif type_name == "binary":
        data = bytes.fromhex(rendered.replace(" ", ""))
    else:
        data = rendered
    if type_name == "dword":
        data = _dword(data)
    if type_name == "binary" and not isinstance(data, (bytes, bytearray)):
        raise RegistryError(f"valor binário inválido: {rendered}")
    return {"type": type_name, "data": _to_json(type_name, data)}


def show(value):
    if value is None:
        return "(apagar)"
    if value["type"] == "dword":
        return f"0x{value['data']:08X}"
    if value["type"] == "binary":
        data = value["data"]
        return data if len(data) <= 24 else f"{data[:24]}… ({len(data) // 2} bytes)"
    return repr(value["data"])

import re
import tomllib
from pathlib import Path

HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
FN_RE = re.compile(r"^(lighten|darken|mix)\((.*)\)$")


class PaletteError(Exception):
    pass


def hex_to_rgb(value):
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


def rgb_to_hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(c))):02X}" for c in rgb)


def _mix(a, b, t):
    ra, rb = hex_to_rgb(a), hex_to_rgb(b)
    return rgb_to_hex(x + (y - x) * t for x, y in zip(ra, rb))


def _resolve_ref(raw, ref):
    ref = ref.strip()
    if HEX_RE.match(ref):
        return ref
    section, _, key = ref.partition(".")
    try:
        value = raw[section][key]
    except KeyError:
        raise PaletteError(f"referência desconhecida: {ref}") from None
    if not (isinstance(value, str) and HEX_RE.match(value)):
        raise PaletteError(f"{ref} não é uma cor #RRGGBB")
    return value


def _compute(raw, expr):
    fn, args = FN_RE.match(expr).groups()
    parts = [p.strip() for p in args.split(",")]
    if fn in ("lighten", "darken") and len(parts) == 2:
        color, amount = _resolve_ref(raw, parts[0]), float(parts[1])
        return _mix(color, "#FFFFFF" if fn == "lighten" else "#000000", amount)
    if fn == "mix" and len(parts) == 3:
        return _mix(_resolve_ref(raw, parts[0]), _resolve_ref(raw, parts[1]), float(parts[2]))
    raise PaletteError(f"expressão inválida: {expr}")


class Palette:
    def __init__(self, path):
        self.path = Path(path)
        with open(self.path, "rb") as f:
            self.raw = tomllib.load(f)
        for section in self.raw.values():
            for key, value in section.items():
                if isinstance(value, str) and FN_RE.match(value):
                    section[key] = _compute(self.raw, value)
        self.id = self.raw["theme"]["id"]
        self.name = self.raw["theme"]["name"]

    def color(self, dotted):
        return _resolve_ref(self.raw, dotted)

    def tokens(self):
        """Placeholders achatados para os templates (ARCHITECTURE.md §4.2)."""
        out = {}
        for section, values in self.raw.items():
            for key, value in values.items():
                name = f"{section}_{key}"
                if isinstance(value, bool):
                    out[name] = "true" if value else "false"
                    continue
                out[name] = str(value)
                if isinstance(value, str) and HEX_RE.match(value):
                    r, g, b = hex_to_rgb(value)
                    out[f"{name}_nohash"] = value[1:]
                    out[f"{name}_rgb"] = f"{r},{g},{b}"
                    out[f"{name}_r"], out[f"{name}_g"], out[f"{name}_b"] = str(r), str(g), str(b)
                elif isinstance(value, float) and 0 < value <= 1:
                    out[f"{name}_pct"] = str(round(value * 100))
        kde = self.raw["kde"]
        out["lnf_id"] = f"org.{self.id}.desktop"
        out["icon_theme"] = f"{self.name}-{kde['icon_base']}"
        out["color_scheme"] = self.name
        return out

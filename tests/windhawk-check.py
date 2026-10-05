#!/usr/bin/env python3
"""W2 targets (windhawk-*): checks that need neither Windhawk nor admin.

For each target with a [windhawk] table, the settings are rendered and turned into YAML in
memory, then:
  - no ${placeholder} is left and every hex color is a palette color (no loose hex);
  - every style is "Property=Value" or "Property:=XAML", and every $Constant it uses is
    defined in styleConstants;
  - the YAML parses back (minimal parser for the subset to_yaml() writes) to the same data;
  - flatten() -> unflatten() is lossless, so the registry layout round-trips;
  - status logic: old settings -> pending, the generated settings "pasted" -> applied,
    and Windhawk's [""] for empty lists does not count as a difference.
Runs on any OS. The real look is in docs/CHECKLIST-W2.md.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tooling import platform, targets  # noqa: E402
from tooling.backends import windhawk  # noqa: E402
from tooling.palette import HEX_RE, Palette  # noqa: E402

failures = []


def check(ok, what):
    print(f"{'ok   ' if ok else 'FALHA'} {what}")
    if not ok:
        failures.append(what)


def parse_yaml(text):
    """Parser for exactly what to_yaml() writes: block maps/lists, single-quoted strings, ints."""
    lines = [ln for ln in text.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]

    def scalar(s):
        s = s.strip()
        if s == "[]":
            return []
        if s.startswith("'"):
            return s[1:-1].replace("''", "'")
        if s in ("true", "false"):
            return s == "true"
        return int(s)

    def block(i, indent):
        if lines[i].startswith(" " * indent + "- "):
            out = []
            while i < len(lines) and lines[i].startswith(" " * indent + "- "):
                rest = lines[i][indent + 2:]
                if re.match(r"^[A-Za-z_][\w]*:", rest):
                    lines[i] = " " * (indent + 2) + rest
                    item, i = block(i, indent + 2)
                else:
                    item, i = scalar(rest), i + 1
                out.append(item)
            return out, i
        out = {}
        while i < len(lines) and len(lines[i]) - len(lines[i].lstrip()) == indent and not lines[i].lstrip().startswith("- "):
            key, _, rest = lines[i].strip().partition(":")
            if rest.strip():
                out[key], i = scalar(rest), i + 1
            else:
                out[key], i = block(i + 1, indent + 2)
        return out, i

    data, _ = block(0, 0)
    return data


def main():
    platform.current = lambda: platform.WINDOWS  # the [windows]-only placeholders
    palette = Palette(ROOT / "palette.toml")
    runner = targets.Runner(ROOT, palette, dry_run=True)
    runner.tokens.update(platform.tokens(palette.id, runner.tokens) or {
        "user_data": "C:/x", "local_appdata": "C:/x", "yasb_config": "C:/x",
        "surface_float_opacity_hexalpha": f"{round(float(runner.tokens['surface_float_opacity']) * 255):02X}"})
    colors = {v.upper() for k, v in runner.tokens.items() if isinstance(v, str) and HEX_RE.match(v)}
    alpha = runner.tokens["surface_float_opacity_hexalpha"]

    found = [t for t in targets.load_targets(ROOT) if "windhawk" in t.meta]
    check(sorted(t.name for t in found) == ["windhawk-explorer", "windhawk-notifications", "windhawk-start"],
          f"alvos W2: {[t.name for t in found]}")
    for target in found:
        spec = target.meta["windhawk"]
        settings = runner._render_tree(spec["settings"], target.name)
        text = windhawk.to_yaml(settings, header=("teste",))
        name = target.name
        check("${" not in text and "$$" not in text, f"{name}: nenhum placeholder sobrando")
        loose = set()
        for h in re.findall(r"#[0-9A-Fa-f]{6,8}\b", text):
            h = h.upper()
            if len(h) == 9:  # #AARRGGBB
                if h[1:3] != alpha:
                    loose.add(h)
                h = "#" + h[3:]
            if h not in colors:
                loose.add(h)
        check(not loose, f"{name}: só cores da paleta {sorted(loose) if loose else ''}")
        consts = {c.split("=", 1)[0] for c in settings.get("styleConstants", []) if c}
        bad, used = [], set()
        for cs in settings.get("controlStyles", []):
            check(bool(cs["target"].strip()), f"{name}: alvo não vazio ({cs['target'][:50]})")
            for style in cs["styles"]:
                if not re.match(r"^[\w.@]+\s*:?=", style):
                    bad.append(style)
                used |= set(re.findall(r"\$(\w+)", style))
        check(not bad, f"{name}: estilos no formato Propriedade=Valor {bad[:2] if bad else ''}")
        check(used <= consts, f"{name}: constantes definidas ({sorted(used - consts)})")
        check(parse_yaml(text) == settings, f"{name}: o YAML volta igual aos dados")
        flat = windhawk.flatten(settings)
        check(windhawk.flatten(windhawk.unflatten(flat)) == flat, f"{name}: formato do registro sem perdas")
        check(windhawk.applied(settings, flat), f"{name}: colado = aplicado")
        old = {"theme": "LiquidGlass", "styleConstants[0]": "", "controlStyles[0].target": ""}
        check(not windhawk.applied(settings, old), f"{name}: configuração antiga = pendente")
        with_empty = dict(flat, **{"themeResourceVariables[0]": ""})
        check(windhawk.applied(settings, with_empty), f"{name}: [\"\"] do Windhawk não conta como diferença")

    print("\nWindhawk OK." if not failures else f"\n{len(failures)} falha(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

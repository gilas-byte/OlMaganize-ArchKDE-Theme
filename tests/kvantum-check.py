#!/usr/bin/env python3
"""Checagens do alvo kvantum (PHASE-2.md §5). Não toca no sistema.

- nenhum #RRGGBB nos templates (toda cor vem de palette.toml);
- generate.py é determinístico e os templates commitados estão em dia com a paleta;
- o SVG renderizado é XML válido e não sobra placeholder;
- cada elemento que o kvconfig referencia existe no SVG (senão o Kvantum cai no tema
  padrão dele, cinza, sem avisar).
"""
import configparser
import hashlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "targets/kvantum"
TEMPLATES = TARGET / "templates"
BUILD = ROOT / "build/kvantum"

failures = []


def check(ok, message):
    print(("PASSOU: " if ok else "FALHOU: ") + message)
    if not ok:
        failures.append(message)


def digest():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(TEMPLATES.iterdir())}


before = digest()
subprocess.run([sys.executable, TARGET / "generate.py"], check=True)
after = digest()
check(after == before, "templates em dia com generate.py e a paleta (rode o render e commite)")
subprocess.run([sys.executable, TARGET / "generate.py"], check=True)
check(digest() == after, "generate.py determinístico")

hexes = [(p.name, m) for p in TEMPLATES.iterdir()
         for m in re.findall(r"#[0-9A-Fa-f]{6}\b", p.read_text())]
check(not hexes, f"nenhum hex solto nos templates {hexes[:3] if hexes else ''}")

subprocess.run([sys.executable, "-m", "tooling", "render", "--only", "kvantum"], cwd=ROOT,
               check=True, stdout=subprocess.DEVNULL)
svg = (BUILD / "theme.svg").read_text()
check("${" not in svg, "SVG renderizado sem placeholder")
ids = {el.get("id") for el in ET.fromstring(svg).iter() if el.get("id")}
check(len(ids) > 400, f"SVG é XML válido ({len(ids)} ids)")

ini = configparser.ConfigParser(interpolation=None, comment_prefixes=(";",), strict=True)
ini.optionxform = str
ini.read_string((BUILD / "theme.kvconfig").read_text())


def spec(section, key):
    """Valor com herança (inherits), como o Kvantum resolve."""
    seen = set()
    while section in ini and section not in seen:
        seen.add(section)
        if key in ini[section]:
            return ini[section][key]
        section = ini[section].get("inherits")
    return None


POSITIONS = ("top", "bottom", "left", "right", "topleft", "topright", "bottomleft", "bottomright")
missing = []
for section in ini.sections():
    if section.startswith("%") or section in ("GeneralColors", "Hacks"):
        continue
    if spec(section, "frame") == "true":
        element = spec(section, "frame.element")
        name = element if section == "Focus" else f"{element}-normal"
        frames = {int(spec(section, f"frame.{side}") or 0) for side in ("top", "left")}
        if frames != {0}:
            missing += [f"[{section}] {name}-{p}" for p in POSITIONS
                        if f"{name}-{p}" not in ids and not (
                            # peças de espessura zero não são desenhadas
                            section == "HeaderSection" and p in ("top", "left", "topleft",
                                                                  "topright", "bottomleft"))]
        if spec(section, "focusFrame") == "true":
            missing += [f"[{section}] {element}-focus-{p}" for p in POSITIONS
                        if f"{element}-focus-{p}" not in ids]
    if spec(section, "interior") == "true":
        element = spec(section, "interior.element")
        if f"{element}-normal" not in ids:
            missing.append(f"[{section}] {element}-normal")
check(not missing, f"elementos do kvconfig existem no SVG {missing[:5] if missing else ''}")

loose = [name for name in ("button-default-indicator", "menu-shadow-hint-top", "menu-shadow-top",
             "checkbox-checked-normal", "radio-checked-normal", "arrow-down-normal",
             "tree-plus-normal", "slidercursor-normal", "progress-pattern-normal")
         if name not in ids]
check(not loose, f"elementos avulsos (indicadores, sombra de menu, check/radio, setas) {loose or ''}")

print("\nKvantum OK." if not failures else f"\n{len(failures)} falha(s).")
sys.exit(1 if failures else 0)

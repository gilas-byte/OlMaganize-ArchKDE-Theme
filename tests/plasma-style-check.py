#!/usr/bin/env python3
"""Checagens do alvo plasma-style (PHASE-3.md §5). Não toca no sistema.

- nenhum #RRGGBB nos templates (toda cor vem de palette.toml);
- generate.py é determinístico e os templates commitados estão em dia com a paleta;
- os SVGs renderizados são XML válido e não sobra placeholder;
- cada arquivo nosso tem todos os prefixos (frames) e elementos que o equivalente do
  tema "default" (Breeze) tem. O fallback do Plasma é por ARQUIVO: se um prefixo falta
  num arquivo que o tema fornece, o Plasma não desenha nada ali.
"""
import gzip
import hashlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "targets/plasma-style"
TEMPLATES = TARGET / "templates"
BUILD = ROOT / "build/plasma-style/theme"
BREEZE = Path("/usr/share/plasma/desktoptheme/default")

# Omissões intencionais, por nome de arquivo.
ALLOWED = {
    # a sombra da tecla fica dentro do frame; mask-normal não é usado pelo Plasma 6
    "button.svg": {"shadow", "mask-normal"},
    # sem focusframe, o foco do campo usa o prefixo "focus"
    "lineedit.svg": {"focusframe"},
    # "blurred" é opcional (plasmoides no desktop com blur do papel de parede);
    # toolbutton-pressed não é usado por nenhum QML do Plasma 6
    "background.svg": {"blurred", "blurred-mask", "toolbutton-pressed"},
}
POS = re.compile(r"-?(topleft|topright|bottomleft|bottomright|top|bottom|left|right|center)$")
# ids de trabalho do Inkscape e grupos auxiliares do Breeze, que o Plasma não lê
NOISE = re.compile(r"^(path|rect|g|defs|svg|stop|linearGradient|radialGradient|filter|fe|"
                   r"metadata|namedview|layer|text|tspan|use|clipPath|mask\d|circle|ellipse|"
                   r"guide|grid|perspective)\d|^(st|sb|sl|sr|[a-g]|msc|pc|base|shadow|true|false|"
                   r"current-color-scheme|shadow-corner|shadow-side)$|^shadow-\w+-\d+$")

failures = []


def check(ok, message):
    print(("PASSOU: " if ok else "FALHOU: ") + message)
    if not ok:
        failures.append(message)


def digest():
    return {p.relative_to(TEMPLATES).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(TEMPLATES.rglob("*")) if p.is_file()}


def elements(text):
    frames, singles = set(), set()
    for i in set(re.findall(r'id="([^"]+)"', text)):
        if NOISE.search(i) or "hint" in i:
            continue
        m = POS.search(i)
        (frames if m else singles).add(i[:m.start()] if m else i)
    return frames, singles


before = digest()
subprocess.run([sys.executable, TARGET / "generate.py"], check=True)
after = digest()
check(after == before, "templates em dia com generate.py e a paleta (rode o render e commite)")
subprocess.run([sys.executable, TARGET / "generate.py"], check=True)
check(digest() == after, "generate.py determinístico")

hexes = [(p.name, m) for p in TEMPLATES.rglob("*") if p.is_file()
         for m in re.findall(r"#[0-9A-Fa-f]{6}\b", p.read_text())]
check(not hexes, f"nenhum hex solto nos templates {hexes[:3] if hexes else ''}")

subprocess.run([sys.executable, "-m", "tooling", "render", "--only", "plasma-style"], cwd=ROOT,
               check=True, stdout=subprocess.DEVNULL)
svgs = sorted(BUILD.rglob("*.svg"))
bad = []
for svg in svgs:
    text = svg.read_text()
    try:
        ET.fromstring(text)
    except ET.ParseError as err:
        bad.append(f"{svg.name}: {err}")
    if "${" in text:
        bad.append(f"{svg.name}: placeholder sobrando")
check(not bad, f"{len(svgs)} SVGs renderizados válidos e sem placeholder {bad[:3] if bad else ''}")

if not BREEZE.is_dir():
    print("AVISO: tema default do Plasma não encontrado; pulando a comparação com o Breeze")
else:
    missing = []
    for svg in svgs:
        rel = svg.relative_to(BUILD)
        breeze = BREEZE / f"{rel}z"
        if not breeze.is_file():
            missing.append(f"{rel}: sem equivalente no Breeze")
            continue
        b_frames, b_singles = elements(gzip.open(breeze).read().decode())
        o_frames, o_singles = elements(svg.read_text())
        allowed = ALLOWED.get(rel.name, set())
        for name in sorted((b_frames - o_frames) | (b_singles - o_singles)):
            if name not in allowed:
                missing.append(f"{rel}: {name}")
    check(not missing, f"prefixos e elementos do Breeze presentes {missing[:5] if missing else ''}")

for rel in ("metadata.json", "plasmarc"):
    check((BUILD / rel).is_file(), f"{rel} renderizado")

print("\nPlasma Style OK." if not failures else f"\n{len(failures)} falha(s).")
sys.exit(1 if failures else 0)

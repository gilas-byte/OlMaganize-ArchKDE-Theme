#!/usr/bin/env python3
"""Gera templates/theme/ do alvo plasma-style (Plasma Style "Gibi").

Roda antes do render (chave "generate" do target.toml), como o gerador do Kvantum:
geometria resolvida aqui a partir de palette.toml, cores como ${tokens}. O fatiamento e
as camadas de tecla/campo vêm de tooling/svgslice.py.

Base: o tema "default" (Breeze) do Plasma, LGPL. Dele vêm os nomes de arquivos,
prefixos, elementos hint-* e as margens (medidas no Plasma 6.7 com QSvgRenderer); o
desenho é refeito aqui. Arquivos que este gerador não escreve caem no Breeze, que já
segue o esquema de cores Gibi.colors.

Não edite templates/theme/ à mão: edite este arquivo e rode
`python3 -m tooling render --only plasma-style`.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from tooling.palette import Palette  # noqa: E402
from tooling.svgslice import (Kit, Paint, Sheet, band, circle, plasma_names,  # noqa: E402
                              ring, rrect, shrink)

PAL = Palette(ROOT / "palette.toml")
KIT = Kit(PAL)
R_S, R_M, R_L, BW = KIT.r_s, KIT.r_m, KIT.r_l, KIT.bw
DROP_Y, DEPTH = KIT.drop_y, KIT.depth
MID = 20
SHADOW = 10          # quanto a sombra de painéis/popups passa da borda (igual ao Breeze)
SHADOW_OVERLAP = 6   # parte da peça de sombra que fica sob a borda (peça de 16px no Breeze)
HEADER = "Gerado por targets/plasma-style/generate.py a partir de palette.toml. Não edite à mão."
KEY = (R_M, R_M, R_M, R_M + DROP_Y)     # L, T, R, B das teclas de tarefa, como no Kvantum
# Botões e campos dos popups usam radius_s: o Plasma desenha a caixa do checkbox com o
# frame "normal" do botão (16px), e com radius_m ela viraria um círculo igual ao radio.
BTN_R = R_S
BTN = (BTN_R, BTN_R, BTN_R, BTN_R + DROP_Y)

solid, rgba = KIT.solid, KIT.rgba
EDGE = solid("base.70")
MASK = solid("base.140")                 # só a forma importa (região do blur)


def hints(sheet, prefix, margins, kind="margin"):
    """Elementos <prefixo>-hint-<lado>-margin: o tamanho relevante é a espessura."""
    lead = f"{prefix}-" if prefix else ""
    left, top, right, bottom = margins
    for side, (w, h) in (("left", (left, 2)), ("top", (2, top)), ("right", (right, 2)),
                         ("bottom", (2, bottom))):
        sheet.simple(f"{lead}hint-{side}-{kind}", max(w, 0.001), max(h, 0.001))


def master(frames):
    left, top, right, bottom = frames
    return left + MID + right, top + MID + bottom


# --- superfícies: painel, popups, dicas ---------------------------------------------------

def surface(sheet, fill, radius, frames, margins, edge=EDGE, shadow=True, mask=True):
    """Frame sem prefixo + mask-* + shadow-*: o esquema de panel-background, dialogs e tooltip."""
    w, h = master(frames)
    body = rrect(0, 0, w, h, radius)
    sheet.nine(plasma_names(), w, h, frames, [([body], fill), (ring((0, 0, w, h), BW, radius), edge)])
    hints(sheet, "", margins)
    if mask:
        sheet.nine(plasma_names("mask"), w, h, frames, [([body], MASK)])
    if shadow:
        s, o = SHADOW, SHADOW_OVERLAP
        side = s + o
        ws, hs = 2 * side + MID, 2 * side + MID
        inner = rrect(s, s, ws - s, hs - s, radius)
        layers = []
        drop = 2  # a sombra "cai" um pouco para baixo, como nos menus do Kvantum
        for k in range(1, s + 1):
            halo = rrect(s - k, s - k + drop, ws - s + k, hs - s + k + drop, radius + k)
            layers.append(([halo, inner], Paint(rgba("shade.strong").fill, "0.03")))
        sheet.nine(plasma_names("shadow"), ws, hs, (side,) * 4, layers)
        hints(sheet, "shadow", (s,) * 4)
        hints(sheet, "shadow", (s,) * 4, kind="inset")


def panel_background(opacity):
    sheet = Sheet(HEADER)
    surface(sheet, solid("base.100", opacity), R_L, (R_L,) * 4, (4,) * 4)
    # prefixo "thick": o Panel.qml lê só as margens dele (espaçamento em barras grossas)
    sheet.simple("thick-center", 5, 5)
    hints(sheet, "thick", (8, 8, 8, 8))
    sheet.simple("hint-tile-center", 5, 5)
    return sheet


def dialog_background(opacity):
    sheet = Sheet(HEADER)
    surface(sheet, solid("base.90", opacity), R_L, (R_L,) * 4, (6,) * 4)
    return sheet


def tooltip(opacity="1"):
    sheet = Sheet(HEADER)
    surface(sheet, solid("base.140", opacity), R_S, (6,) * 4, (4,) * 4)
    return sheet


def widget_background(opacity):
    """Fundo de plasmoides no desktop e de menus/popups dos Plasma Components."""
    sheet = Sheet(HEADER)
    surface(sheet, solid("base.90", opacity), R_L, (R_L,) * 4, (8,) * 4)
    return sheet


def plasmoid_heading():
    sheet = Sheet(HEADER)
    frames = (6,) * 4
    w, h = master(frames)
    fill = solid("base.110", KIT.float_opacity)
    head = rrect(0, 0, w, h, (R_L, R_L, 0, 0))
    sheet.nine(plasma_names("header"), w, h, frames,
               [([head], fill), (band(head, h - BW, h), EDGE)])
    foot = rrect(0, 0, w, h, (0, 0, R_L, R_L))
    sheet.nine(plasma_names("footer"), w, h, frames,
               [([foot], fill), (band(foot, 0, BW), EDGE)])
    hints(sheet, "", (6, 6, 6, 6))
    sheet.simple("hint-stretch-borders", 5, 5)
    return sheet


# --- teclas: tarefas e botões ------------------------------------------------------------

def face_only(w, h, face, r):
    """Sobreposição de hover do botão: troca só a face da tecla (a base continua)."""
    bottom = h - DROP_Y
    body = rrect(0, 0, w, bottom, r)
    inner = rrect(BW, BW, w - BW, bottom - BW, shrink(r, BW))
    outline = ring((0, 0, w, bottom), BW, r)
    return [(band(body, 0, bottom - DEPTH), face), (band(inner, BW, BW + 1), KIT.highlight),
            (band(outline[0], 0, bottom - DEPTH) + band(outline[1], 0, bottom - DEPTH),
             KIT.border)]


def attention_key(w, h):
    """Tecla com borda e base amarelas: o mesmo sinal do botão padrão da fase 2."""
    bottom = h - DROP_Y
    body = rrect(0, 0, w, bottom, R_M)
    accent = solid("accent.primary")
    return KIT.keycap(w, h, KIT.face) + [
        (band(body, bottom - DEPTH, bottom), accent),
        (band(body, bottom - DEPTH, bottom), KIT.base),
        (ring((0, 0, w, bottom), BW, R_M), accent),
    ]


def tasks():
    sheet = Sheet(HEADER)
    w, h = master(KEY)
    states = {
        "normal": [],
        "hover": KIT.keycap(w, h, KIT.hover),
        # janela ativa: tecla com face roxa-escura; com base.90 ficava igual ao hover
        "focus": KIT.keycap(w, h, solid("selection.bg_subtle")),
        "attention": attention_key(w, h),
        "minimized": KIT.keycap(w, h, solid("base.110", "0.6"), "disabled"),
        "progress": [([rrect(0, 0, w, h - DROP_Y, R_M)], solid("accent.secondary", "0.35"))],
    }
    # sem prefixo = barra embaixo; north = em cima; west/east = laterais. A tecla é a mesma.
    for location in ("", "north", "west", "east"):
        for state, layers in states.items():
            prefix = f"{location}-{state}" if location else state
            sheet.nine(plasma_names(prefix), w, h, KEY, layers)
            hints(sheet, prefix, (4,) * 4)
    # selo de tarefas agrupadas (o Breeze usa o mesmo desenho nas 4 posições)
    n = 11
    for side in ("top", "bottom", "left", "right"):
        sheet.simple(f"group-expander-{side}", n, n,
                     [([circle(n / 2, n / 2, n / 2)], solid("accent.secondary")),
                      (ring((0, 0, n, n), BW, n / 2), KIT.border)],
                     _stroke("M5.5,3 L5.5,8 M3,5.5 L8,5.5", "base.10", 1.5))
    return sheet


def button():
    sheet = Sheet(HEADER)
    w, h = master(BTN)
    sheet.nine(plasma_names("normal"), w, h, BTN, KIT.keycap(w, h, KIT.face, r=BTN_R))
    sheet.nine(plasma_names("pressed"), w, h, BTN, KIT.keycap(w, h, KIT.sunk, "pressed", r=BTN_R))
    sheet.nine(plasma_names("hover"), w, h, BTN, face_only(w, h, KIT.hover, BTN_R))
    sheet.nine(plasma_names("focus"), w, h, BTN, KIT.focus_ring(w, h, BTN_R))
    # botões planos (ToolButton): sem fundo em repouso, tecla inteira no hover
    sheet.nine(plasma_names("toolbutton-hover"), w, h, BTN, KIT.keycap(w, h, KIT.hover, r=BTN_R))
    sheet.nine(plasma_names("toolbutton-pressed"), w, h, BTN,
               KIT.keycap(w, h, KIT.sunk, "pressed", r=BTN_R))
    sheet.nine(plasma_names("toolbutton-focus"), w, h, BTN, KIT.focus_ring(w, h, BTN_R))
    for prefix in ("normal", "pressed"):
        hints(sheet, prefix, (6,) * 4)
    for prefix in ("toolbutton-hover", "toolbutton-pressed"):
        hints(sheet, prefix, (4,) * 4)
    for prefix in ("hover", "focus", "toolbutton-focus"):
        hints(sheet, prefix, (0,) * 4)
    return sheet


def action_button():
    """Botões redondos (RoundButton, Dial): círculo com cara de tecla."""
    sheet = Sheet(HEADER)
    for size in (32, 24, 22, 16):
        lead = "" if size == 32 else f"{size}-{size}-"
        rad = (size - DROP_Y) / 2
        cx = size / 2
        body = circle(cx, rad, rad)
        inner = circle(cx, rad, rad - BW)
        pressed = circle(cx, rad + KIT.PRESS, rad)
        sheet.simple(f"{lead}normal", size, size, [
            ([circle(cx, rad + DROP_Y, rad)], rgba("keycap.drop", 0.6)), ([body], KIT.face),
            (band(body, 2 * rad - DEPTH, 2 * rad), KIT.base), (band(inner, BW, BW + 1), KIT.highlight),
            ([body, inner], KIT.border)])
        sheet.simple(f"{lead}pressed", size, size, [
            ([pressed], KIT.sunk), ([pressed, circle(cx, rad + KIT.PRESS, rad - BW)], KIT.border)])
        sheet.simple(f"{lead}hover", size, size,
                     [(band(body, 0, 2 * rad - DEPTH), KIT.hover), ([body, inner], KIT.border)])
        sheet.simple(f"{lead}focus", size, size,
                     [(ring((cx - rad, 0, cx + rad, 2 * rad), KIT.ring_width, rad), KIT.focus)])
    return sheet


# --- campos, listas, abas ----------------------------------------------------------------

def lineedit():
    sheet = Sheet(HEADER)
    w, h = master(BTN)
    bottom = h - DROP_Y
    sheet.nine(plasma_names("base"), w, h, BTN, KIT.field(w, h, KIT.field_bg, r=BTN_R))
    sheet.nine(plasma_names("hover"), w, h, BTN,
               [(ring((0, 0, w, bottom), BW, BTN_R), solid("base.50"))])
    sheet.nine(plasma_names("focus"), w, h, BTN, KIT.focus_ring(w, h, BTN_R))
    hints(sheet, "base", (6,) * 4)
    hints(sheet, "hover", (0,) * 4)
    hints(sheet, "focus", (0,) * 4)
    sheet.simple("hint-focus-over-base", 2, 2)
    return sheet


def viewitem():
    sheet = Sheet(HEADER)
    frames = (R_S,) * 4
    w, h = master(frames)
    body = rrect(0, 0, w, h, R_S)
    inner = rrect(BW, BW, w - BW, h - BW, R_S - BW)
    selected = [([body], solid("selection.bg")),
                (band(body, h - 2, h), rgba("keycap.base_color", 0.6)),
                (band(inner, BW, BW + 1), KIT.highlight),
                ([body, inner], KIT.border)]
    sheet.nine(plasma_names("normal"), w, h, frames, [])
    sheet.nine(plasma_names("hover"), w, h, frames, [([body], solid("base.70", "0.5"))])
    sheet.nine(plasma_names("selected"), w, h, frames, selected)
    sheet.nine(plasma_names("selected+hover"), w, h, frames,
               selected + [([body], rgba("keycap.highlight", 0.5))])
    return sheet


def tabbar():
    """Aba ativa: só a linha amarela de 2px do lado do conteúdo."""
    sheet = Sheet(HEADER)
    frames = (4, 4, 4, 4)
    w, h = master(frames)
    line = KIT.ring_width
    accent = solid("accent.primary")
    sides = {"north": (0, h - line, w, h), "south": (0, 0, w, line),
             "west": (w - line, 0, w, h), "east": (0, 0, line, h)}
    margins = {"north": (6, 10, 6, 10), "south": (6, 10, 6, 10),
               "west": (4, 6, 8, 6), "east": (8, 6, 4, 6)}
    for side, (x0, y0, x1, y1) in sides.items():
        prefix = f"{side}-active-tab"
        sheet.nine(plasma_names(prefix), w, h, frames, [([rrect(x0, y0, x1, y1, 0)], accent)])
        hints(sheet, prefix, margins[side])
    return sheet


# --- indicadores: checkbox, radio, switch, slider, rolagem, progresso ---------------------

CHECK = "M4,8 L7,11 L12.5,5"


def _stroke(d, color, width=2):
    section, key = color.split(".")
    return (f'<path d="{d}" fill="none" stroke="${{{section}_{key}}}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def checkmarks():
    """A caixa do checkbox é o frame "normal" do botão; aqui só o "ligado" por cima."""
    sheet = Sheet(HEADER)
    n = 16
    bottom = n - DROP_Y
    box = rrect(0, 0, n, bottom, R_S)
    sheet.simple("checkbox", n, n, [([box], solid("accent.secondary")),
                                    (ring((0, 0, n, bottom), BW, R_S), KIT.border)],
                 _stroke("M4.5,7 L7,9.5 L11.5,4.5", "base.10"))
    dot = circle(n / 2, bottom / 2, 3)
    sheet.simple("radiobutton", n, n, [([dot], solid("accent.secondary"))])
    return sheet


def radiobutton():
    sheet = Sheet(HEADER)
    n = 16
    c = circle(n / 2, n / 2, n / 2)
    cring = [c, circle(n / 2, n / 2, n / 2 - BW)]
    sheet.simple("normal", n, n, [([c], KIT.field_bg), (cring, EDGE)])
    sheet.simple("hover", n, n, [(cring, solid("base.50"))])
    sheet.simple("checked", n, n, [([c], solid("accent.secondary")), (cring, KIT.border),
                                   ([circle(n / 2, n / 2, 3)], solid("base.10"))])
    f = n + 2 * KIT.ring_width
    sheet.simple("focus", f, f, [(ring((0, 0, f, f), KIT.ring_width, f / 2), KIT.focus)])
    sheet.simple("shadow", n + 6, n + 6)
    sheet.simple("hint-size", n, n)
    sheet.simple("symbol", 6, 6, [([circle(3, 3, 3)], solid("base.10"))])
    return sheet


def _knob(size, face, pressed=False):
    """Alça redonda com cara de tecla (switch e slider)."""
    rad = (size - DROP_Y) / 2
    cx = size / 2
    if pressed:
        body = circle(cx, rad + KIT.PRESS, rad)
        return [([body], face), ([body, circle(cx, rad + KIT.PRESS, rad - BW)], KIT.border)]
    body = circle(cx, rad, rad)
    inner = circle(cx, rad, rad - BW)
    return [([circle(cx, rad + DROP_Y, rad)], rgba("keycap.drop", 0.6)), ([body], face),
            (band(body, 2 * rad - DEPTH + 1, 2 * rad), KIT.base),
            (band(inner, BW, BW + 1), KIT.highlight), ([body, inner], KIT.border)]


def switch():
    sheet = Sheet(HEADER)
    bar_h = 16
    side = bar_h / 2
    w = 2 * side + 5
    for state, fill in (("inactive", KIT.field_bg), ("active", solid("accent.secondary"))):
        pill = rrect(0, 0, w, bar_h, side)
        sheet.nine(plasma_names(state), w, bar_h, (side, 0, side, 0),
                   [([pill], fill), (ring((0, 0, w, bar_h), BW, side), KIT.border)])
    sheet.simple("hint-bar-size", 38, bar_h)
    sheet.simple("hint-stretch-borders", 4, 4)
    knob = 22
    sheet.simple("handle", knob, knob, _knob(knob, solid("base.40")))
    sheet.simple("handle-hover", knob, knob, _knob(knob, solid("base.20")))
    sheet.simple("handle-pressed", knob, knob, _knob(knob, solid("base.50"), pressed=True))
    f = knob + 4
    sheet.simple("handle-focus", f, f, [(ring((2, 0, f - 2, f - 4), KIT.ring_width, (f - 4) / 2),
                                         KIT.focus)])
    sheet.simple("handle-shadow", knob + 6, knob + 6)
    return sheet


def slider():
    sheet = Sheet(HEADER)
    r = 3
    w, h = 2 * r + 2, 2 * r + 2
    for prefix, fill in (("groove", KIT.field_bg), ("groove-highlight", solid("accent.secondary"))):
        sheet.nine(plasma_names(prefix), w, h, (r,) * 4, [([rrect(0, 0, w, h, r)], fill)])
    size = 20
    for orient in ("horizontal", "vertical"):
        sheet.simple(f"{orient}-slider-handle", size, size, _knob(size, solid("base.70")))
        sheet.simple(f"{orient}-slider-hover", size, size,
                     [(band(circle(size / 2, (size - DROP_Y) / 2, (size - DROP_Y) / 2), 0,
                            size - DROP_Y - DEPTH), solid("base.60"))])
        f = size + 4
        sheet.simple(f"{orient}-slider-focus", f, f,
                     [(ring((2, 2, f - 2, f - 2 - DROP_Y), KIT.ring_width, (f - 4 - DROP_Y) / 2),
                       KIT.focus)])
        sheet.simple(f"{orient}-slider-shadow", size + 6, size + 6)
    sheet.simple("hint-handle-size", size, size)
    return sheet


def scrollbar():
    """Pílula fina sem trilho visível, como no Kvantum."""
    sheet = Sheet(HEADER)
    r = 3
    w, h = 2 * r + 2, 2 * r + 2
    for prefix, fill in (("slider", solid("base.70")), ("mouseover-slider", solid("base.60"))):
        sheet.nine(plasma_names(prefix), w, h, (r,) * 4, [([rrect(0, 0, w, h, r)], fill)])
        hints(sheet, prefix, (6, 3, 6, 3), kind="inset")
    for orient in ("horizontal", "vertical"):
        prefix = f"background-{orient}"
        sheet.nine(plasma_names(prefix), w, h, (r,) * 4, [])
        hints(sheet, prefix, (6, 3, 6, 3), kind="inset")
    sheet.simple("hint-scrollbar-size", 6, 6)
    return sheet


def bar_meter():
    sheet = Sheet(HEADER)
    r = 3
    w, h = 2 * r + 2, 2 * r + 2
    sheet.nine(plasma_names("bar-inactive"), w, h, (r,) * 4,
               [([rrect(0, 0, w, h, r)], KIT.field_bg)])
    sheet.nine(plasma_names("bar-active"), w, h, (r,) * 4,
               [([rrect(0, 0, w, h, r)], solid("accent.secondary"))])
    sheet.simple("hint-bar-size", 6, 6)
    return sheet


# --- montagem ----------------------------------------------------------------------------

def files():
    """Caminho relativo ao tema -> conteúdo."""
    fl = KIT.float_opacity
    svgs = {
        # painel: widgets/ = com composição sem blur; translucent/ = com blur;
        # solid/ = opaco (painel no modo opaco ou sem composição)
        "widgets/panel-background.svg": panel_background(fl),
        "translucent/widgets/panel-background.svg": panel_background(fl),
        "solid/widgets/panel-background.svg": panel_background("1"),
        "opaque/widgets/panel-background.svg": panel_background("1"),
        "dialogs/background.svg": dialog_background(fl),
        "translucent/dialogs/background.svg": dialog_background(fl),
        "solid/dialogs/background.svg": dialog_background("1"),
        "opaque/dialogs/background.svg": dialog_background("1"),
        "widgets/tooltip.svg": tooltip(),
        "translucent/widgets/tooltip.svg": tooltip(),
        "solid/widgets/tooltip.svg": tooltip(),
        "opaque/widgets/tooltip.svg": tooltip(),
        "widgets/background.svg": widget_background(fl),
        "translucent/widgets/background.svg": widget_background(fl),
        "solid/widgets/background.svg": widget_background("1"),
        "widgets/plasmoidheading.svg": plasmoid_heading(),
        "widgets/tasks.svg": tasks(),
        "widgets/button.svg": button(),
        "widgets/actionbutton.svg": action_button(),
        "widgets/lineedit.svg": lineedit(),
        "widgets/viewitem.svg": viewitem(),
        "widgets/tabbar.svg": tabbar(),
        "widgets/checkmarks.svg": checkmarks(),
        "widgets/radiobutton.svg": radiobutton(),
        "widgets/switch.svg": switch(),
        "widgets/slider.svg": slider(),
        "widgets/scrollbar.svg": scrollbar(),
        "widgets/bar_meter_horizontal.svg": bar_meter(),
    }
    out = {path: sheet.render() for path, sheet in svgs.items()}
    # O Plasma guarda os SVGs renderizados em cache por nome + versão do tema. A versão
    # leva um hash dos templates e da paleta, então qualquer mudança invalida o cache.
    digest = hashlib.sha256((ROOT / "palette.toml").read_bytes())
    for path in sorted(out):
        digest.update(path.encode() + out[path].encode())
    out["plasmarc"] = PLASMARC
    digest.update(PLASMARC.encode())
    out["metadata.json"] = json.dumps({
        "KPlugin": {
            "Authors": [{"Name": "${theme_name}"}],
            "Description": "Marrons quentes e teclas. Paleta do Primary for Obsidian (Cecilia May); "
                           "estrutura do Breeze (KDE VDG, LGPL).",
            "Id": "${theme_name}",
            "License": "GPL-3.0-or-later",
            "Name": "${theme_name}",
            "Version": "1." + str(int(digest.hexdigest()[:8], 16)),
        },
        "X-Plasma-API-Minimum-Version": "6.0",
    }, indent=4, ensure_ascii=False) + "\n"
    return out


PLASMARC = """# Blur do KWin atrás de painéis e popups translúcidos; sem o efeito de contraste,
# que puxaria as cores para longe da paleta.
[ContrastEffect]
enabled=false

[BlurBehindEffect]
enabled=true

[AdaptiveTransparency]
enabled=true
"""


def write_if_changed(path, content):
    if path.is_file() and path.read_text() == content:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def main():
    out = HERE / "templates/theme"
    wanted = files()
    for rel, content in wanted.items():
        write_if_changed(out / rel, content)
    for stale in sorted(out.rglob("*"), reverse=True):
        rel = stale.relative_to(out).as_posix()
        if stale.is_file() and rel not in wanted:
            stale.unlink()
        elif stale.is_dir() and not any(stale.iterdir()):
            stale.rmdir()


if __name__ == "__main__":
    main()

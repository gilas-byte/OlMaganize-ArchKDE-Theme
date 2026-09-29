#!/usr/bin/env python3
"""Gera templates/theme.svg e templates/theme.kvconfig do alvo kvantum.

Roda automaticamente antes do render (chave "generate" do target.toml). A geometria
(raios, profundidade da tecla, sombra, anel de foco) vem de palette.toml e é resolvida
aqui; as cores saem como ${tokens} e só viram hex no render. Assim nenhum hex solto
mora nos templates e mudar um raio na paleta redesenha o tema.

O Kvantum desenha cada widget com até 9 objetos por estado, esticando cada um para o
tamanho das bordas definido no kvconfig. O fatiamento e as camadas de tecla/campo moram
em tooling/svgslice.py (compartilhado com o alvo plasma-style).

Não edite templates/theme.svg nem templates/theme.kvconfig à mão: edite este arquivo
ou theme.kvconfig.in e rode `python3 -m tooling render --only kvantum`.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from tooling.palette import Palette  # noqa: E402
from tooling.svgslice import (Kit, Paint, Sheet, band, circle, clip, num as _num,  # noqa: E402
                              ring, rrect, shrink as _shrink)

PAL = Palette(ROOT / "palette.toml")
RAW = PAL.raw
KIT = Kit(PAL)

R_S, R_M, R_L = KIT.r_s, KIT.r_m, KIT.r_l
BW = KIT.bw
DEPTH = KIT.depth
DROP_Y = KIT.drop_y
RING = KIT.ring_width
PRESS = KIT.PRESS          # quanto a face da tecla desce quando pressionada
MENU_SHADOW = 8            # menu_shadow_depth
SCROLL_WIDTH = 10          # scroll_width; a alça é uma pílula mais fina, centralizada
SCROLL_PILL = 6
SLIDER_WIDTH = 6           # trilho do slider
HANDLE = 16                # alça do slider e tamanho de checkbox/radio
ARROW = 9                  # indicator.size das setas
MID = 20                   # tamanho da fatia central nas peças mestres (qualquer valor serve)

solid, rgba = KIT.solid, KIT.rgba
keycap, focus_ring, field, flat = KIT.keycap, KIT.focus_ring, KIT.field, KIT.flat
FACE, HOVER, SUNK, FIELD = KIT.face, KIT.hover, KIT.sunk, KIT.field_bg
BORDER, SHADE, BASE, HIGHLIGHT = KIT.border, KIT.shade, KIT.base, KIT.highlight
FOCUS, FLOAT_OPACITY = KIT.focus, KIT.float_opacity

KEY_FRAMES = (R_M, R_M, R_M, R_M + DROP_Y)     # L, T, R, B das teclas e campos


def buttons(sheet):
    frames = KEY_FRAMES
    w, h = frames[0] + MID + frames[2], frames[1] + MID // 2 + frames[3]
    for state, face in (("normal", FACE), ("focused", HOVER), ("pressed", SUNK),
                        ("toggled", solid("selection.bg")), ("disabled", FIELD)):
        sheet.nine(f"button-{state}", w, h, frames, keycap(w, h, face, state))
    # Botão padrão: o Kvantum desenha button-default POR CIMA do estado atual e usa a mesma
    # cor de texto de todos os botões (não há text color para o default). Com a face
    # amarela o texto bege ficaria ilegível, então o amarelo vai na borda e na base da
    # tecla; o interior fica vazio para o hover/pressionado continuarem visíveis.
    bottom = h - DROP_Y
    body = rrect(0, 0, w, bottom, R_M)
    accent = solid("accent.primary")
    sheet.nine("button-default", w, h, frames, [
        (band(body, bottom - DEPTH, bottom), accent),
        (band(body, bottom - DEPTH, bottom), BASE),
        (ring((0, 0, w, bottom), BW, R_M), accent),
    ], interior=False)
    sheet.simple("button-default", MID, MID // 2)
    sheet.nine("button-focus", w, h, frames, focus_ring(w, h), interior=False)
    sheet.simple("button-default-indicator", 8, 8)


def fields(sheet):
    frames = KEY_FRAMES
    w, h = frames[0] + MID + frames[2], frames[1] + MID // 2 + frames[3]
    sheet.nine("lineedit-normal", w, h, frames, field(w, h, FIELD))
    sheet.nine("lineedit-focused", w, h, frames, field(w, h, FIELD, focused=True))
    # combo não editável: normal, hover, pressionado (foco de teclado ou lista aberta)
    sheet.nine("combo-normal", w, h, frames, field(w, h, FIELD))
    sheet.nine("combo-focused", w, h, frames, field(w, h, SUNK))
    sheet.nine("combo-pressed", w, h, frames, field(w, h, FIELD, focused=True))
    sheet.nine("combo-toggled", w, h, frames, field(w, h, FIELD, focused=True))


def item_views(sheet):
    f = R_S
    w, h = 2 * f + MID, 2 * f + MID // 2
    frames = (f, f, f, f)
    sheet.nine("itemview-normal", w, h, frames, [])
    sheet.nine("itemview-focused", w, h, frames, flat(w, h, solid("base.70", "0.5")))
    sheet.nine("itemview-pressed", w, h, frames, flat(w, h, solid("selection.bg")))
    body = rrect(0, 0, w, h, R_S)
    inner = rrect(BW, BW, w - BW, h - BW, R_S - BW)
    selected = [([body], solid("selection.bg")),
                (band(body, h - 2, h), rgba("keycap.base_color", 0.6)),
                (band(inner, BW, BW + 1), HIGHLIGHT),
                ([body, inner], BORDER)]
    sheet.nine("itemview-toggled", w, h, frames, selected)
    sheet.nine("itemview-toggled-inactive", w, h, frames, flat(w, h, solid("selection.bg_subtle")))


def tabs(sheet):
    f = R_S
    w, h = 2 * f + MID, 2 * f + MID // 2
    frames = (f, f, f, f)
    top = (R_S, R_S, 0, 0)
    for state, face in (("normal", SUNK), ("focused", FACE)):
        sheet.nine(f"tab-{state}", w, h, frames, [([rrect(0, 0, w, h, top)], face)])
    active = rrect(0, 0, w, h, top)
    underline = [([active], solid("base.100")),
                 (band(active, h - RING, h), solid("accent.primary"))]
    sheet.nine("tab-toggled", w, h, frames, underline)
    sheet.nine("tab-pressed", w, h, frames, underline)
    sheet.nine("tabframe-normal", w, h, frames,
               [(ring((0, 0, w, h), BW, R_S), solid("base.80"))], interior=False)
    for state, color in (("normal", "base.40"), ("focused", "base.10"), ("pressed", "base.20"),
                         ("toggled", "base.40"), ("disabled", "base.60")):
        sheet.simple(f"tab-close-{state}", ARROW, ARROW,
                     extra=_stroke("M2,2 L7,7 M7,2 L2,7", color))


def scrollbars(sheet):
    inset = (SCROLL_WIDTH - SCROLL_PILL) / 2
    r = SCROLL_PILL / 2
    side = inset + r
    w, h = 2 * side + 2, 2 * r + MID
    frames = (side, r, side, r)
    for state, color in (("normal", "base.70"), ("focused", "base.60"), ("pressed", "base.60")):
        sheet.nine(f"scrollbarslider-{state}", w, h, frames,
                   [([rrect(inset, 0, w - inset, h, r)], solid(color))])
    sheet.simple("scrollbargroove-normal", 10, 20)
    for state in ("normal", "focused", "pressed"):
        sheet.simple(f"grip-{state}", 8, 8)


def sliders(sheet):
    r = SLIDER_WIDTH / 2
    w, h = 2 * r + 2, 2 * r + MID
    frames = (r, r, r, r)
    sheet.nine("slider-normal", w, h, frames, [([rrect(0, 0, w, h, r)], FIELD)])
    sheet.nine("slider-toggled", w, h, frames,
               [([rrect(0, 0, w, h, r)], solid("accent.secondary"))])
    sheet.simple("slider-tick-normal", 5, 1, [([rrect(0, 0, 5, 1, 0)], solid("base.60"))])
    # Alça: tecla em miniatura (círculo). Face mais clara que a das teclas: a alça é
    # pequena e sumiria sobre base.100.
    rad = (HANDLE - DROP_Y) / 2
    for state, face in (("normal", solid("base.70")), ("focused", solid("base.60")),
                        ("pressed", HOVER), ("disabled", FIELD)):
        sheet.simple(f"slidercursor-{state}", HANDLE, HANDLE, _round_key(rad, face, state))


def _round_key(rad, face, state):
    cx, top = HANDLE / 2, 0
    bottom = top + 2 * rad
    if state == "pressed":
        body = circle(cx, top + PRESS + rad, rad)
        inner = circle(cx, top + PRESS + rad, rad - BW)
        return [([body], face), ([body, inner], BORDER)]
    body = circle(cx, top + rad, rad)
    inner = circle(cx, top + rad, rad - BW)
    if state == "disabled":
        return [([body], face), ([body, inner], BORDER)]
    return [([circle(cx, top + rad + DROP_Y, rad)], rgba("keycap.drop", 0.6)),
            ([body], face),
            (band(body, bottom - DEPTH + 1, bottom), BASE),  # base 1px menor, escala da alça
            (band(inner, top + BW, top + BW + 1), HIGHLIGHT),
            ([body, inner], BORDER)]


def progress(sheet):
    f = R_S
    w, h = 2 * f + MID, 2 * f + MID // 2
    frames = (f, f, f, f)
    sheet.nine("progress-normal", w, h, frames, field(w, h, FIELD, r=R_S, drop=0))
    bar = rrect(0, 0, w, h, R_S)
    inner = rrect(BW, BW, w - BW, h - BW, R_S - BW)
    sheet.nine("progress-pattern-normal", w, h, frames,
               [([bar], solid("accent.secondary")), (band(inner, BW, BW + 1), HIGHLIGHT),
                ([bar, inner], BORDER)])


def menus(sheet):
    s, f = MENU_SHADOW, R_L
    menu_fill = solid("base.90", FLOAT_OPACITY)
    edge = solid("base.70")
    # com composição: sombra + borda nas peças menu-shadow-*, interior em menu-normal
    w, h = 2 * (s + f) + MID, 2 * (s + f) + MID
    body = rrect(s, s, w - s, h - s, R_L)
    layers = []
    offset = 2  # sombra "cai" para baixo
    for k in range(1, s + 1):
        halo = rrect(s - k, s - k + offset, w - s + k, h - s + k + offset, R_L + k)
        layers.append(([clip(halo, (0, 0, w, h)), body], Paint(rgba("shade.strong").fill, "0.035")))
    layers += [([body], menu_fill), (ring((s, s, w - s, h - s), BW, R_L), edge)]
    sheet.nine("menu-shadow", w, h, (s + f,) * 4, layers, interior=False)
    # sem composição: o mesmo menu sem sombra, com as espessuras normais do frame
    w2, h2 = 2 * f + MID, 2 * f + MID
    sheet.nine("menu-normal", w2, h2, (f,) * 4,
               [([rrect(0, 0, w2, h2, R_L)], menu_fill), (ring((0, 0, w2, h2), BW, R_L), edge)])
    for side, (w3, h3) in (("top", (10, s)), ("bottom", (10, s)), ("left", (s, 10)),
                           ("right", (s, 10))):
        sheet.simple(f"menu-shadow-hint-{side}", w3, h3)

    fi = R_S
    w4, h4 = 2 * fi + MID, 2 * fi + MID // 2
    frames = (fi, fi, fi, fi)
    hover = flat(w4, h4, solid("selection.bg_subtle"))
    sheet.nine("menuitem-normal", w4, h4, frames, [])
    for state in ("focused", "pressed", "toggled"):
        sheet.nine(f"menuitem-{state}", w4, h4, frames, hover)
    sheet.simple("menuitem-separator", 20, 9, [([rrect(0, 4, 20, 5, 0)], edge)])
    sheet.nine("menubaritem-normal", w4, h4, frames, [])
    for state in ("focused", "pressed", "toggled"):
        sheet.nine(f"menubaritem-{state}", w4, h4, frames, hover)


def tooltips_and_frames(sheet):
    f = R_S
    w, h = 2 * f + MID, 2 * f + MID // 2
    frames = (f, f, f, f)
    sheet.nine("tooltip-normal", w, h, frames,
               flat(w, h, solid("base.140"), border=solid("base.70")))
    # moldura genérica (em volta de views): anel sutil, faixa interna na cor da view
    common = [([rrect(0, 0, w, h, R_S)], solid("base.100")),
              (ring((0, 0, w, h), BW, R_S), solid("base.80"))]
    sheet.nine("common-normal", w, h, frames, common, interior=False)
    sheet.nine("common-focused", w, h, frames, common[:1] + [
        (ring((0, 0, w, h), BW, R_S), solid("base.70"))], interior=False)
    sheet.nine("group-normal", w, h, frames,
               [(ring((0, 0, w, h), BW, R_S), solid("base.80"))], interior=False)
    # anel de foco genérico (rótulos de checkbox, radio, abas): no máximo 2px
    fr = RING
    w2, h2 = 2 * fr + MID, 2 * fr + MID // 2
    sheet.nine("focus", w2, h2, (fr,) * 4, [(ring((0, 0, w2, h2), RING, fr), FOCUS)],
               interior=False)


def headers(sheet):
    w, h = MID, MID // 2 + 1
    frames = (0, 0, 1, 1)
    for state, face in (("normal", SUNK), ("focused", FACE), ("pressed", HOVER),
                        ("toggled", SUNK)):
        sheet.nine(f"header-{state}", w, h, frames,
                   [([rrect(0, 0, w, h, 0)], face), ([rrect(0, h - 1, w, h, 0)], solid("base.70"))])
    sheet.simple("header-separator", 1, 20, [([rrect(0, 4, 1, 16, 0)], solid("base.70"))])


def checks(sheet):
    n = HANDLE
    mark = _stroke("M4,8.5 L7,11.5 L12.5,5", "base.10", 2)
    dash = _stroke("M4.5,8 L11.5,8", "base.10", 2)
    box = rrect(0, 0, n, n, R_S)
    boxring = ring((0, 0, n, n), BW, R_S)
    lift = ([box], Paint("${keycap_highlight_hex}", "${keycap_highlight_alpha}"))
    off = {
        "normal": [([box], FIELD), (boxring, solid("base.70"))],
        "focused": [([box], SUNK), (boxring, solid("base.50"))],
        "pressed": [([box], SUNK), (boxring, solid("base.70"))],
    }
    on = [([box], solid("accent.secondary")), (boxring, BORDER)]
    on_states = {"normal": on, "focused": on + [lift], "pressed": on}
    for state in ("normal", "focused", "pressed"):
        sheet.simple(f"checkbox-{state}", n, n, off[state])
        sheet.simple(f"checkbox-checked-{state}", n, n, on_states[state], mark)
        sheet.simple(f"checkbox-tristate-{state}", n, n, on_states[state], dash)
    dim = RAW["keycap"]["disabled_opacity"]
    sheet.simple("checkbox-disabled", n, n, off["normal"], opacity=dim)
    sheet.simple("checkbox-checked-disabled", n, n, on, mark, opacity=dim)
    sheet.simple("checkbox-tristate-disabled", n, n, on, dash, opacity=dim)

    c = circle(n / 2, n / 2, n / 2)
    cring = [c, circle(n / 2, n / 2, n / 2 - BW)]
    dot = ([circle(n / 2, n / 2, 3)], solid("base.10"))
    roff = {
        "normal": [([c], FIELD), (cring, solid("base.70"))],
        "focused": [([c], SUNK), (cring, solid("base.50"))],
        "pressed": [([c], SUNK), (cring, solid("base.70"))],
    }
    ron = [([c], solid("accent.secondary")), (cring, BORDER), dot]
    ron_states = {"normal": ron, "focused": ron[:2] + [([c], lift[1]), dot], "pressed": ron}
    for state in ("normal", "focused", "pressed"):
        sheet.simple(f"radio-{state}", n, n, roff[state])
        sheet.simple(f"radio-checked-{state}", n, n, ron_states[state])
    sheet.simple("radio-disabled", n, n, roff["normal"], opacity=dim)
    sheet.simple("radio-checked-disabled", n, n, ron, opacity=dim)


def _stroke(d, color, width=1.5):
    section, key = color.split(".")
    return (f'<path d="{d}" fill="none" stroke="${{{section}_{key}}}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


ARROW_STATES = (("normal", "base.40"), ("focused", "base.20"), ("pressed", "base.10"),
                ("toggled", "base.10"), ("disabled", "base.60"))
CHEVRONS = {
    "up": "M1.5,6 L4.5,3 L7.5,6",
    "down": "M1.5,3 L4.5,6 L7.5,3",
    "left": "M6,1.5 L3,4.5 L6,7.5",
    "right": "M3,1.5 L6,4.5 L3,7.5",
    "plus": "M4.5,1.5 L4.5,7.5 M1.5,4.5 L7.5,4.5",
    "minus": "M1.5,4.5 L7.5,4.5",
}


def arrows(sheet):
    for direction, d in CHEVRONS.items():
        for state, color in ARROW_STATES:
            sheet.simple(f"arrow-{direction}-{state}", ARROW, ARROW, extra=_stroke(d, color))
    # árvore: fechado = seta para a direita, aberto = para baixo
    for kind, d in (("plus", CHEVRONS["right"]), ("minus", CHEVRONS["down"])):
        for state, color in ARROW_STATES:
            if state != "toggled":
                sheet.simple(f"tree-{kind}-{state}", ARROW, ARROW, extra=_stroke(d, color))


def misc(sheet):
    dots = "".join(f'<circle cx="3.5" cy="{y}" r="1" fill="${{base_60}}"/>' for y in (6, 10, 14))
    sheet.simple("toolbar-handle", 8, 20, extra=dots)
    sheet.simple("toolbar-separator", 7, 20, [([rrect(3, 3, 4, 17, 0)], solid("base.70"))])
    sheet.simple("splitter-normal", 7, 20)
    for state, color in (("normal", "base.70"), ("focused", "base.50"), ("pressed", "base.40")):
        grip = "".join(f'<circle cx="3.5" cy="{y}" r="1" fill="${{{color.replace(".", "_")}}}"/>'
                       for y in (4, 8, 12))
        sheet.simple(f"splitter-grip-{state}", 7, 16, extra=grip)
    for state, color in (("normal", "base.60"), ("focused", "base.40")):
        grip = "".join(f'<circle cx="{x}" cy="{y}" r="1" fill="${{{color.replace(".", "_")}}}"/>'
                       for x, y in ((11, 5), (11, 8), (8, 8), (11, 11), (8, 11), (5, 11)))
        sheet.simple(f"resize-grip-{state}", 13, 13, extra=grip)
    sheet.simple("dial", 32, 32, [([circle(16, 16, 16)], FIELD),
                                  (ring((0, 0, 32, 32), BW, 16), solid("base.70"))])
    sheet.simple("dial-notches", 32, 32)
    sheet.simple("dial-handle", 8, 8, [([circle(4, 4, 4)], solid("accent.secondary"))])


def build_svg():
    sheet = Sheet("Gerado por targets/kvantum/generate.py a partir de palette.toml. "
                  "Não edite à mão.")
    for part in (buttons, fields, item_views, tabs, scrollbars, sliders, progress, menus,
                 tooltips_and_frames, headers, checks, arrows, misc):
        part(sheet)
    return sheet.render()


# --- kvconfig ----------------------------------------------------------------------------

GEOMETRY = {
    "key_left": KEY_FRAMES[0], "key_top": KEY_FRAMES[1], "key_right": KEY_FRAMES[2],
    "key_bottom": KEY_FRAMES[3],
    "small": R_S, "menu_frame": R_L, "menu_shadow": MENU_SHADOW, "menu_blur": min(R_L, 10),
    "focus": RING,
    "scroll_width": SCROLL_WIDTH, "scroll_side": _num((SCROLL_WIDTH - SCROLL_PILL) / 2
                                                      + SCROLL_PILL / 2),
    "scroll_end": _num(SCROLL_PILL / 2),
    "slider_width": SLIDER_WIDTH, "slider_frame": _num(SLIDER_WIDTH / 2), "handle": HANDLE,
    "arrow": ARROW,
}


def build_kvconfig():
    src = (HERE / "theme.kvconfig.in").read_text()

    def sub(m):
        key = m.group(1)
        if key not in GEOMETRY:
            raise SystemExit(f"generate: theme.kvconfig.in usa @{key}@ desconhecido")
        return str(GEOMETRY[key])

    return re.sub(r"@(\w+)@", sub, src)


def write_if_changed(path, content):
    if path.is_file() and path.read_text() == content:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def main():
    out = HERE / "templates"
    write_if_changed(out / "theme.svg", build_svg())
    write_if_changed(out / "theme.kvconfig", build_kvconfig())


if __name__ == "__main__":
    main()

from .palette import hex_to_rgb

AA = 4.5
FAINT = 3.0

# (texto, fundo, mínimo). Pares obrigatórios de ARCHITECTURE.md §5.3.
REQUIRED = [
    ("base.20", "base.100", AA),
    ("base.10", "base.100", AA),
    ("base.40", "base.100", AA),
    ("base.20", "base.110", AA),
    ("accent.on_primary", "accent.primary", AA),
    ("selection.fg", "selection.bg", AA),
]

# Pares informativos: só avisam. base.60 é texto desabilitado (isento no WCAG).
ADVISORY = [
    ("base.20", "base.120", AA),
    ("base.20", "base.90", AA),
    ("base.40", "base.110", AA),
    ("base.50", "base.100", FAINT),
    ("base.60", "base.100", FAINT),
    ("selection.fg", "selection.bg_subtle", AA),
]


def _luminance(hex_color):
    def channel(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in hex_to_rgb(hex_color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    a, b = sorted((_luminance(fg), _luminance(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def check(palette, out=print):
    failed = False
    for pairs, required in ((REQUIRED, True), (ADVISORY, False)):
        out("Pares obrigatórios:" if required else "Pares informativos:")
        for fg, bg, minimum in pairs:
            r = ratio(palette.color(fg), palette.color(bg))
            ok = r >= minimum
            tag = "ok" if ok else ("FALHA" if required else "aviso")
            out(f"  {tag:<5} {fg:>18} sobre {bg:<14} {r:5.2f}:1 (mín {minimum})")
            failed |= required and not ok
    return not failed

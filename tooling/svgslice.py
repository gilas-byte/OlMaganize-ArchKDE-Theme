"""Desenho de temas SVG fatiados em 9 peças (Kvantum, Plasma Style).

Kvantum e Plasma Style desenham cada widget com até 9 objetos por estado (4 cantos,
4 bordas e o centro), esticando cada um até o tamanho das bordas. Aqui um elemento é
descrito como camadas de retângulos arredondados numa "peça mestre", fatiada nas 9
partes por recorte de polígono. O QtSvg (SVG Tiny 1.2, usado pelo Kvantum e pelo KSvg)
não entende clipPath, filtros nem rgba(), por isso tudo vira <path> com fill-opacity.

As cores saem como ${tokens} e só viram hex no render; a geometria (raios, profundidade
da tecla...) vem da paleta e é resolvida aqui.
"""
import math

from .palette import parse_rgba, parse_shadow

POSITIONS = (("topleft", "top", "topright"), ("left", None, "right"),
             ("bottomleft", "bottom", "bottomright"))


def num(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


# --- cores -------------------------------------------------------------------------------

class Paint:
    def __init__(self, fill, opacity="1"):
        self.fill, self.opacity = fill, opacity


# --- geometria ---------------------------------------------------------------------------

def rrect(x0, y0, x1, y1, r):
    """Polígono de um retângulo arredondado. r: número ou (tl, tr, br, bl)."""
    radii = (r, r, r, r) if isinstance(r, (int, float)) else r
    w, h = x1 - x0, y1 - y0
    radii = [max(0.0, min(c, w / 2, h / 2)) for c in radii]
    tl, tr, br, bl = radii
    pts = []
    for cx, cy, rad, start in ((x0 + tl, y0 + tl, tl, 180), (x1 - tr, y0 + tr, tr, 270),
                               (x1 - br, y1 - br, br, 0), (x0 + bl, y1 - bl, bl, 90)):
        if rad <= 0:
            pts.append((cx, cy))
            continue
        steps = max(3, math.ceil(rad * 1.5))
        for i in range(steps + 1):
            a = math.radians(start + 90 * i / steps)
            pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    return pts


def circle(cx, cy, r):
    return rrect(cx - r, cy - r, cx + r, cy + r, r)


def clip(poly, box):
    """Sutherland–Hodgman: interseção de um polígono com um retângulo."""
    x0, y0, x1, y1 = box
    edges = (
        (lambda p: p[0] >= x0, lambda a, b: _cross_x(a, b, x0)),
        (lambda p: p[0] <= x1, lambda a, b: _cross_x(a, b, x1)),
        (lambda p: p[1] >= y0, lambda a, b: _cross_y(a, b, y0)),
        (lambda p: p[1] <= y1, lambda a, b: _cross_y(a, b, y1)),
    )
    out = poly
    for inside, cross in edges:
        if not out:
            break
        pts, out = out, []
        prev = pts[-1]
        for cur in pts:
            if inside(cur):
                if not inside(prev):
                    out.append(cross(prev, cur))
                out.append(cur)
            elif inside(prev):
                out.append(cross(prev, cur))
            prev = cur
    return out


def _cross_x(a, b, x):
    t = (x - a[0]) / (b[0] - a[0])
    return (x, a[1] + t * (b[1] - a[1]))


def _cross_y(a, b, y):
    t = (y - a[1]) / (b[1] - a[1])
    return (a[0] + t * (b[0] - a[0]), y)


def _area(poly):
    return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(poly, poly[1:] + poly[:1]))) / 2


def shrink(r, d):
    if isinstance(r, (int, float)):
        return max(0, r - d)
    return tuple(max(0, c - d) for c in r)


def ring(outer, width, r):
    """Anel interno de espessura `width` em um retângulo arredondado (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = outer
    return [rrect(x0, y0, x1, y1, r), rrect(x0 + width, y0 + width, x1 - width, y1 - width,
                                            shrink(r, width))]


def band(poly, y0, y1, x0=-1e6, x1=1e6):
    return [clip(poly, (x0, y0, x1, y1))]


# --- saída SVG ---------------------------------------------------------------------------

def kvantum_names(base):
    """Kvantum: interior = base, bordas = base-<pos>."""
    return lambda pos: base if pos is None else f"{base}-{pos}"


def plasma_names(prefix=""):
    """Plasma Style: <prefixo>-<pos>, centro = <prefixo>-center (sem prefixo: <pos>)."""
    lead = f"{prefix}-" if prefix else ""
    return lambda pos: f"{lead}{pos or 'center'}"


class Sheet:
    """Folha SVG: cada elemento é um <g id> com um retângulo invisível que fixa a caixa."""

    WIDTH = 900

    def __init__(self, header):
        self.header = header
        self.parts = []
        self.x = self.y = 10
        self.row = 0
        self.ids = set()

    def _place(self, w, h):
        if self.x + w > self.WIDTH:
            self.x, self.y, self.row = 10, self.y + self.row + 10, 0
        pos = (self.x, self.y)
        self.x += w + 10
        self.row = max(self.row, h)
        return pos

    def _group(self, eid, ox, oy, w, h, body):
        if eid in self.ids:
            raise SystemExit(f"generate: id repetido {eid}")
        self.ids.add(eid)
        self.parts.append(
            f'<g id="{eid}" transform="translate({num(ox)},{num(oy)})">'
            f'<rect width="{num(w)}" height="{num(h)}" fill="none"/>{body}</g>')

    @staticmethod
    def _paths(layers, box, dx=0, dy=0):
        out = []
        for shapes, paint in layers:
            polys = [clip(p, box) for p in shapes]
            polys = [p for p in polys if len(p) >= 3 and _area(p) > 1e-4]
            if not polys:
                continue
            d = " ".join("M" + " L".join(f"{num(x - dx)},{num(y - dy)}" for x, y in p) + "Z"
                         for p in polys)
            rule = ' fill-rule="evenodd"' if len(polys) > 1 else ""
            out.append(f'<path d="{d}" fill="{paint.fill}" fill-opacity="{paint.opacity}"{rule}/>')
        return "".join(out)

    def nine(self, names, w, h, frames, layers, interior=True):
        """Fatia uma peça mestre w×h em 9 (frames = L, T, R, B).

        names: str (convenção do Kvantum, base / base-<pos>) ou função pos -> id, com
        pos None para o centro (ver kvantum_names, plasma_names).
        """
        if isinstance(names, str):
            names = kvantum_names(names)
        left, top, right, bottom = frames
        gap = 2
        ox, oy = self._place(w + 2 * gap, h + 2 * gap)
        xs, ys = (0, left, w - right, w), (0, top, h - bottom, h)
        for j in range(3):
            for i in range(3):
                box = (xs[i], ys[j], xs[i + 1], ys[j + 1])
                pw, ph = box[2] - box[0], box[3] - box[1]
                pos = POSITIONS[j][i]
                if pw <= 0 or ph <= 0 or (pos is None and not interior):
                    continue
                body = self._paths(layers, box, box[0], box[1])
                self._group(names(pos), ox + box[0] + i * gap, oy + box[1] + j * gap, pw, ph, body)

    def simple(self, eid, w, h, layers=(), extra="", opacity=None):
        ox, oy = self._place(w, h)
        body = self._paths(layers, (0, 0, w, h)) + extra
        if opacity is not None:
            body = f'<g opacity="{opacity}">{body}</g>'
        self._group(eid, ox, oy, w, h, body)

    def render(self):
        height = self.y + self.row + 10
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.WIDTH}" '
                f'height="{height}" viewBox="0 0 {self.WIDTH} {height}">\n'
                f'<!-- {self.header} -->\n' + "\n".join(self.parts) + "\n</svg>\n")


# --- camadas derivadas da paleta ---------------------------------------------------------

class Kit:
    """Tokens da paleta e as camadas de tecla/campo/anel usadas por todos os geradores."""

    PRESS = 1  # quanto a face da tecla desce quando pressionada

    def __init__(self, palette):
        raw = self.raw = palette.raw
        self.r_s = raw["shape"]["radius_s"]
        self.r_m = raw["shape"]["radius_m"]
        self.r_l = raw["shape"]["radius_l"]
        self.bw = raw["shape"]["border_width"]
        self.depth = raw["keycap"]["base_depth"]
        _, self.drop_y, self.drop_blur, _ = parse_shadow(raw["keycap"]["drop"])
        self.ring_width = raw["focus"]["ring_width"]

        self.face = self.solid("base.90")
        self.hover = self.solid("base.80")
        self.sunk = self.solid("base.110")
        self.field_bg = self.solid("base.120")
        self.border = self.rgba("shape.border_color")
        self.shade = self.rgba("shape.border_color", 0.5)  # linha interna de campo afundado
        self.base = self.rgba("keycap.base_color")
        self.highlight = self.rgba("keycap.highlight")
        self.focus = Paint("${accent_primary}", "${focus_ring_opacity}")
        self.float_opacity = "${surface_float_opacity}"

    def solid(self, dotted, opacity="1"):
        """Cor #RRGGBB da paleta: ${secao_chave}."""
        section, key = dotted.split(".")
        value = self.raw[section][key]
        if not isinstance(value, str) or not value.startswith("#"):
            raise SystemExit(f"generate: {dotted} não é cor #RRGGBB")
        return Paint(f"${{{section}_{key}}}", str(opacity))

    def rgba(self, dotted, scale=None):
        """Token rgba(...): cor em ${x_hex}; opacidade em ${x_alpha} ou alpha*scale."""
        section, key = dotted.split(".")
        value = self.raw[section][key]
        parsed = parse_shadow(value)
        alpha = parsed[3][3] if parsed else parse_rgba(value)[3]
        name = f"{section}_{key}"
        opacity = f"${{{name}_alpha}}" if scale is None else num(alpha * scale)
        return Paint(f"${{{name}_hex}}", opacity)

    def keycap(self, w, h, face, state="normal", r=None):
        """Camadas de uma tecla. Base inferior e sombra só nos estados "em pé"."""
        r = self.r_m if r is None else r
        bw, press = self.bw, self.PRESS
        bottom = h - self.drop_y
        if state in ("pressed", "toggled"):
            body = rrect(0, press, w, bottom, r)
            inner = rrect(bw, press + bw, w - bw, bottom - bw, shrink(r, bw))
            return [([body], face),
                    (band(inner, press + bw, press + bw + 1), self.shade),
                    ([body, inner], self.border)]
        body = rrect(0, 0, w, bottom, r)
        inner = rrect(bw, bw, w - bw, bottom - bw, shrink(r, bw))
        if state == "disabled":
            return [([body], face), ([body, inner], self.border)]
        return [
            # sombra externa curta: duas camadas deslocadas imitam o blur
            ([rrect(0, 1, w, bottom + 1, r)], self.rgba("keycap.drop", 0.5)),
            ([rrect(0.5, self.drop_y, w - 0.5, bottom + self.drop_y, r)],
             self.rgba("keycap.drop", 0.6)),
            ([body], face),
            (band(body, bottom - self.depth, bottom), self.base),
            (band(inner, bw, bw + 1), self.highlight),
            ([body, inner], self.border),
        ]

    def focus_ring(self, w, h, r=None, drop=None):
        r = self.r_m if r is None else r
        drop = self.drop_y if drop is None else drop
        return [(ring((0, 0, w, h - drop), self.ring_width, r), self.focus)]

    def field(self, w, h, face, focused=False, r=None, drop=None):
        """Campo "afundado": sem base inferior nem sombra, linha interna escura no topo."""
        r = self.r_m if r is None else r
        drop = self.drop_y if drop is None else drop
        bw = self.bw
        bottom = h - drop
        body = rrect(0, 0, w, bottom, r)
        inner = rrect(bw, bw, w - bw, bottom - bw, shrink(r, bw))
        layers = [([body], face), (band(inner, bw, bw + 1), self.shade), ([body, inner], self.border)]
        if focused:
            layers += self.focus_ring(w, h, r, drop)
        return layers

    def flat(self, w, h, paint, r=None, border=None):
        r = self.r_s if r is None else r
        body = rrect(0, 0, w, h, r)
        layers = [([body], paint)]
        if border is not None:
            layers.append((ring((0, 0, w, h), self.bw, r), border))
        return layers

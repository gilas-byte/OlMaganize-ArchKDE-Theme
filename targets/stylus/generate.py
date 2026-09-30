#!/usr/bin/env python3
"""Build the stylus target from the Catppuccin userstyles (PHASE-4.md §4).

Runs before the render ("generate" in target.toml). Pipeline:

  1. render the lib (lib.less.in -> templates/lib.less): a single flavor, `gibi`, whose
     26 slots (+ `primary`) point at palette tokens.

Deterministic and only rewrites files whose content changed, like the other generators.
Do not edit templates/lib.less by hand: edit lib.less.in or this file and run
`python3 -m tooling render --only stylus`.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from tooling.palette import Palette  # noqa: E402
from tooling.render import write_if_changed  # noqa: E402

PAL = Palette(ROOT / "palette.toml")
TEMPLATES = HERE / "templates"
FLAVOR = PAL.id

# Lib slot -> palette token (PHASE-4.md §5). Order = the upstream lib's order, plus `primary`
# (the vivid yellow, offered as the "Amarelo vivo" accent). mauve and lavender keep their
# names because the styles reference them, but they are not purple here.
SLOTS = (
    ("rosewater", "web.rosewater"), ("flamingo", "web.flamingo"), ("pink", "sem.pink"),
    ("mauve", "accent.secondary"), ("red", "sem.red"), ("maroon", "web.maroon"),
    ("peach", "sem.orange"), ("yellow", "sem.yellow"), ("green", "sem.green"),
    ("teal", "web.teal"), ("sky", "web.sky"), ("sapphire", "web.sapphire"),
    ("blue", "sem.blue"), ("lavender", "base.40"), ("text", "base.10"),
    ("subtext1", "base.20"), ("subtext0", "web.subtext0"), ("overlay2", "base.40"),
    ("overlay1", "base.50"), ("overlay0", "base.60"), ("surface2", "base.70"),
    ("surface1", "base.80"), ("surface0", "base.90"), ("base", "base.100"),
    ("mantle", "base.120"), ("crust", "base.140"), ("primary", "accent.primary"),
)


def placeholder(token):
    return "${" + token.replace(".", "_") + "}"


def flavor_map(values):
    body = " ".join(f"@{slot}: {value};" for slot, value in values)
    return f"  @{FLAVOR}: {{ {body} }};"


def render_lib():
    """Step 1: lib.less.in -> templates/lib.less, colors as ${tokens}."""
    lib = (HERE / "lib.less.in").read_text()
    lib = lib.replace("@@PALETTE@@", flavor_map((s, placeholder(t)) for s, t in SLOTS))
    lib = lib.replace("@@FILTERS@@", flavor_map((s, "none") for s, _ in SLOTS))
    write_if_changed(TEMPLATES / "lib.less", lib)
    return lib


def main():
    render_lib()


if __name__ == "__main__":
    main()

import argparse
import sys
from pathlib import Path

from . import backup, contrast, icons, targets
from .palette import Palette, PaletteError
from .render import RenderError

ROOT = Path(__file__).resolve().parent.parent


def _only(values):
    names = []
    for v in values or []:
        names += [n.strip() for n in v.split(",") if n.strip()]
    return names


def cmd_render(palette, args):
    all_targets = targets.load_targets(ROOT)
    runner = targets.Runner(ROOT, palette)
    for target in targets.select(all_targets, _only(args.only)) if args.only else all_targets:
        runner.render(target)
        print(f"renderizado: {target.name}")
    return True


def cmd_check(palette, args):
    ok = contrast.check(palette)
    print("\nContraste OK." if ok else "\nContraste insuficiente em par obrigatório.")
    return ok


def cmd_list(palette, args):
    runner = targets.Runner(ROOT, palette)
    for target in targets.load_targets(ROOT):
        detected = "detectado" if runner.detect(target) else "não detectado"
        repo, aur = target.packages()
        missing = targets.missing_packages(repo + aur)
        deps = f", faltam: {', '.join(missing)}" if missing else ""
        extra = " (só com --only)" if target.hidden else ""
        print(f"  {target.order:>3}  {target.name:<12} {detected}{deps}{extra}  — {target.description}")
    return True


def cmd_apply(palette, args):
    if args.list:
        return cmd_list(palette, args)
    selected = targets.select(targets.load_targets(ROOT), _only(args.only))
    if not contrast.check(palette, out=lambda *_: None):
        contrast.check(palette)
        print("\nAbortado: contraste insuficiente (ver ARCHITECTURE.md §3.4).")
        return False
    if args.dry_run:
        print("DRY-RUN: nada no sistema será alterado.")
    return targets.run(ROOT, palette, selected, dry_run=args.dry_run)


def cmd_restore(palette, args):
    only = _only(args.only) or None
    if args.dry_run:
        print("DRY-RUN: nada será restaurado. Restauraria:")
    return backup.restore(palette.id, only=only, dry_run=args.dry_run, cwd=ROOT)


def cmd_icon_theme(palette, args):
    name, base = palette.tokens()["icon_theme"], palette.raw["kde"]["icon_base"]
    if args.action == "get":
        print(icons.current(name))
    elif args.value:
        icons.build(name, base, args.value)
    else:
        icons.remove(name)
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m tooling")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("render", help="renderiza templates em build/")
    p.add_argument("--only", action="append")
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("check", help="verifica contraste WCAG da paleta")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("list", help="lista alvos")
    p.set_defaults(func=cmd_list)

    for name, func, help_ in (("apply", cmd_apply, "aplica os alvos"),
                              ("restore", cmd_restore, "restaura os backups")):
        p = sub.add_parser(name, help=help_)
        p.add_argument("--only", action="append", help="alvo(s), separados por vírgula")
        p.add_argument("--dry-run", action="store_true")
        if name == "apply":
            p.add_argument("--list", action="store_true")
        p.set_defaults(func=func)

    p = sub.add_parser("icon-theme", help="(interno) gera/remove o tema de ícones derivado")
    p.add_argument("action", choices=["get", "set"])
    p.add_argument("value", nargs="?", default="")
    p.set_defaults(func=cmd_icon_theme)

    args = parser.parse_args(argv)
    try:
        palette = Palette(ROOT / "palette.toml")
        ok = args.func(palette, args)
    except (PaletteError, RenderError, targets.TargetError) as err:
        print(f"erro: {err}", file=sys.stderr)
        return 1
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

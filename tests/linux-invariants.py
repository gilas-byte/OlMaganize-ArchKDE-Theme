#!/usr/bin/env python3
"""The Windows work (W1) must not change Linux behavior: checks that run on any OS.

Forces tooling.platform to "linux" and checks that:
  - the Linux targets run in the same order as before W1, and no Windows target sneaks in;
  - each Linux target's meta is its raw target.toml minus `platforms` and `[windows]`;
  - Runner._mode() keeps the declared mode (symlink stays symlink on Linux);
  - the Runner's tokens are exactly Palette.tokens() (no Windows-only placeholders);
  - state_dir() is still $XDG_STATE_HOME/<id> or ~/.local/state/<id>;
  - managed blocks still use plain read_text/write_text (newline=None).

This does NOT replace tests/selftest.sh on a real Arch + KDE machine: it only proves the new
code paths are inert on Linux.
"""
import os
import sys
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tooling import backup, platform, targets  # noqa: E402
from tooling.palette import Palette  # noqa: E402

# Linux targets and their order before W1 (README "Alvos"); _selftest only runs with --only.
LINUX_TARGETS = ["fonts", "kde-colors", "klassy", "kvantum", "kvantum-qt5", "blur", "plasma-style",
                 "gtk", "ghostty", "icons", "brave", "stylus", "lookandfeel"]

failures = []


def check(ok, what):
    print(f"{'ok   ' if ok else 'FALHA'} {what}")
    if not ok:
        failures.append(what)


def main():
    platform.current = lambda: platform.LINUX
    palette = Palette(ROOT / "palette.toml")
    all_targets = targets.load_targets(ROOT)

    selected = [t.name for t in targets.select(all_targets, [])]
    check(selected == LINUX_TARGETS, f"ordem dos alvos no Linux: {selected}")
    windows_only = [t.name for t in all_targets if not t.supported]
    check(all(n.startswith(("win", "yasb", "_selftest-win")) for n in windows_only),
          f"alvos só-Windows pulados no Linux: {windows_only}")

    for target in all_targets:
        if not target.supported:
            continue
        with open(target.dir / "target.toml", "rb") as f:
            raw = tomllib.load(f)
        expected = {k: v for k, v in raw.items() if k not in ("platforms", "windows")}
        got = {k: v for k, v in target.meta.items() if k != "platforms"}
        check(got == expected, f"{target.name}: meta igual ao target.toml sem [windows]")
        for spec in target.meta.get("files", []):
            check(targets.Runner._mode(spec) == spec.get("mode", "symlink"),
                  f"{target.name}: modo {spec.get('mode', 'symlink')} mantido ({spec['dest']})")

    runner = targets.Runner(ROOT, palette, dry_run=True)
    check(runner.tokens == palette.tokens(), "tokens do Runner == Palette.tokens()")
    check(platform.tokens(palette.id) == {}, "nenhum placeholder extra no Linux")

    old = os.environ.pop("XDG_STATE_HOME", None)
    try:
        check(backup.state_dir(palette.id) == Path.home() / ".local/state" / palette.id,
              "state_dir sem XDG_STATE_HOME")
        os.environ["XDG_STATE_HOME"] = "/tmp/xdg-state"
        check(backup.state_dir(palette.id) == Path("/tmp/xdg-state") / palette.id,
              "state_dir com XDG_STATE_HOME")
    finally:
        os.environ.pop("XDG_STATE_HOME", None)
        if old is not None:
            os.environ["XDG_STATE_HOME"] = old

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "f.conf"
        path.write_bytes(b"a\r\nb\n")
        _, newline = backup.read_text_keep_newlines(path)
        check(newline is None, "bloco gerenciado usa read_text/write_text no Linux")

    check(platform.expand("~/x") == os.path.expanduser("~/x"), "expand(): só ~ no Linux")
    check(platform.expand("%LOCALAPPDATA%/x") == "%LOCALAPPDATA%/x", "expand(): %VAR% intocado no Linux")

    print("\nInvariantes do Linux OK." if not failures else f"\n{len(failures)} falha(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

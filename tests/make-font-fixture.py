#!/usr/bin/env python3
"""Write targets/_selftest-win/fixtures/fake-font.zip and print its SHA-256.

The "font" is a minimal sfnt with only a `name` table: enough for tooling/backends/fonts.py
to read the full name, and harmless if AddFontResourceW sees it (Windows rejects it). The zip
is deterministic (fixed timestamps), so the SHA-256 in targets/_selftest-win/target.toml stays
valid; rerun this only if the fixture has to change, and update the hash there.
"""
import hashlib
import io
import struct
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "targets/_selftest-win/fixtures/fake-font.zip"


def name_table(names):
    records, strings = [], b""
    for name_id, text in sorted(names.items()):
        data = text.encode("utf-16-be")
        records.append(struct.pack(">6H", 3, 1, 0x409, name_id, len(data), len(strings)))
        strings += data
    header = struct.pack(">HHH", 0, len(records), 6 + 12 * len(records))
    return header + b"".join(records) + strings


def sfnt(names):
    table = name_table(names)
    offset = 12 + 16
    directory = struct.pack(">IHHHH", 0x00010000, 1, 16, 0, 0)
    record = struct.pack(">4sIII", b"name", 0, offset, len(table))
    return directory + record + table


def main():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as z:
        for style in ("Regular", "Bold"):
            info = zipfile.ZipInfo(f"fonts/GibiSelftest-{style}.ttf", date_time=(2026, 1, 1, 0, 0, 0))
            z.writestr(info, sfnt({1: "Gibi Selftest", 2: style, 4: f"Gibi Selftest {style}"}))
        info = zipfile.ZipInfo("fonts/README.txt", date_time=(2026, 1, 1, 0, 0, 0))
        z.writestr(info, "not a font; must be ignored by the glob\n")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(buf.getvalue())
    print(hashlib.sha256(buf.getvalue()).hexdigest())


if __name__ == "__main__":
    main()

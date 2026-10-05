"""Per-user font install on Windows, no admin (docs/SPIKE-S0.md §3).

A [[fonts]] entry in target.toml names an archive (official release URL, or a path relative
to the target), its SHA-256 and a glob of the font files inside it. Each file is copied to
%LOCALAPPDATA%\\Microsoft\\Windows\\Fonts and registered under
HKCU\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Fonts as "<full name> (TrueType)",
which is exactly what Windows does for "Install for me". AddFontResourceW makes the font
usable right away, without logoff.
"""
import fnmatch
import hashlib
import shutil
import struct
import tarfile
import tempfile
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

from .. import platform

FONTS_KEY = r"HKCU\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
MACHINE_FONTS_KEY = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
FONT_SUFFIXES = (".ttf", ".otf", ".ttc")


class FontError(Exception):
    pass


def fonts_dir():
    return platform.local_appdata() / "Microsoft" / "Windows" / "Fonts"


def cache_dir(theme_id):
    return platform.local_appdata() / theme_id / "cache" / "fonts"


def _is_url(source):
    return urllib.parse.urlparse(source).scheme in ("http", "https", "file")


def cache_path(theme_id, source, sha256):
    name = Path(urllib.parse.urlparse(source).path).name
    return cache_dir(theme_id) / f"{sha256[:16]}-{name}"


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def locate(theme_id, source, sha256, target_dir):
    """Path of the archive if it is already available locally (no download), else None."""
    if not _is_url(source):
        path = Path(target_dir) / source
        return path if path.is_file() else None
    path = cache_path(theme_id, source, sha256)
    return path if path.is_file() and _sha256(path) == sha256 else None


def fetch(theme_id, source, sha256):
    """Download `source` into the cache and check its SHA-256. Returns the cached path."""
    dest = cache_path(theme_id, source, sha256)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=dest.parent, delete=False, suffix=".part") as tmp:
        try:
            with urllib.request.urlopen(source, timeout=60) as response:
                shutil.copyfileobj(response, tmp)
        except OSError as err:
            tmp.close()
            Path(tmp.name).unlink(missing_ok=True)
            raise FontError(f"falha ao baixar {source}: {err}") from None
    got = _sha256(tmp.name)
    if got != sha256:
        Path(tmp.name).unlink(missing_ok=True)
        raise FontError(f"SHA-256 não confere para {source}: esperado {sha256}, veio {got}")
    Path(tmp.name).replace(dest)
    return dest


def members(archive, pattern):
    """[(basename, bytes)] of the font files in `archive` matching `pattern`, sorted."""
    archive = Path(archive)
    out = {}
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as z:
            for name in z.namelist():
                if fnmatch.fnmatchcase(name, pattern) and name.lower().endswith(FONT_SUFFIXES):
                    out[Path(name).name] = z.read(name)
    else:
        with tarfile.open(archive) as t:
            for m in t.getmembers():
                if m.isfile() and fnmatch.fnmatchcase(m.name, pattern) and m.name.lower().endswith(FONT_SUFFIXES):
                    out[Path(m.name).name] = t.extractfile(m).read()
    if not out:
        raise FontError(f"nenhum arquivo casa com {pattern!r} em {archive.name}")
    return sorted(out.items())


def _names(data):
    """{name_id: str} from the `name` table (Windows platform, en-US)."""
    # In a collection (.ttc) the first font's header sits at an offset; table offsets are
    # absolute in both cases.
    header = data[struct.unpack(">I", data[12:16])[0]:] if data[:4] == b"ttcf" else data
    (count,) = struct.unpack(">H", header[4:6])
    for i in range(count):
        tag, _, offset, length = struct.unpack(">4sIII", header[12 + 16 * i:28 + 16 * i])
        if tag == b"name":
            table = data[offset:offset + length]
            _, n, strings = struct.unpack(">HHH", table[:6])
            out = {}
            for j in range(n):
                pid, eid, lid, nid, ln, off = struct.unpack(">6H", table[6 + 12 * j:18 + 12 * j])
                if pid == 3 and lid == 0x409:
                    out[nid] = table[strings + off:strings + off + ln].decode("utf-16-be")
            return out
    raise FontError("arquivo de fonte sem tabela 'name'")


def value_name(data):
    """Registry value name Windows uses for a font: "<full name> (TrueType)"."""
    try:
        names = _names(data)
    except (struct.error, UnicodeDecodeError) as err:
        raise FontError(f"tabela 'name' ilegível: {err}") from None
    full = names.get(4) or " ".join(filter(None, (names.get(1), names.get(2))))
    if not full:
        raise FontError("fonte sem nome completo")
    return f"{full} (TrueType)"


def machine_has(name):
    """True if the font is already installed for all users (HKLM, read-only)."""
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, MACHINE_FONTS_KEY) as key:
            winreg.QueryValueEx(key, name)
        return True
    except FileNotFoundError:
        return False


def same_file(path, data):
    path = Path(path)
    return path.is_file() and path.stat().st_size == len(data) and path.read_bytes() == data

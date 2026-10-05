import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from . import blocks, kde, platform


def state_dir(theme_id):
    return platform.state_dir(theme_id)


def _identity(entry):
    kind = entry["kind"]
    if kind in ("file", "block"):
        return (kind, entry["path"])
    if kind == "key":
        return (kind, entry["file"], tuple(entry["group"]), entry["key"])
    if kind == "registry":
        return (kind, entry["key"], entry["name"])
    if kind == "font":
        return (kind, entry["path"])
    return (kind, entry["target"], entry["name"])


def read_text_keep_newlines(path):
    """(text, newline) of a user file. On Windows the newline style is kept on write-back, so
    a managed block never converts a whole LF file to CRLF. Elsewhere newline is None and
    behavior is unchanged (read_text/write_text)."""
    path = Path(path)
    if not platform.is_windows():
        return path.read_text(), None
    raw = path.read_bytes()
    return path.read_text(), "\r\n" if b"\r\n" in raw else "\n"


def write_text_newlines(path, text, newline):
    if newline is None:
        Path(path).write_text(text)
    else:
        with open(path, "w", newline=newline) as f:
            f.write(text)


def remove_path(path):
    path = Path(path)
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def copy_path(src, dest):
    src, dest = Path(src), Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_symlink():
        dest.symlink_to(os.readlink(src))
    elif src.is_dir():
        shutil.copytree(src, dest, symlinks=True)
    else:
        shutil.copy2(src, dest)


class BackupSession:
    """Um diretório de backup por execução, criado só quando algo muda de fato."""

    def __init__(self, theme_id):
        self.root = state_dir(theme_id) / "backups"
        self.dir = None
        self.entries = []
        self.seen = set()

    def _ensure(self):
        if self.dir is None:
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            self.dir = self.root / stamp
            (self.dir / "files").mkdir(parents=True)

    def _save(self):
        tmp = self.dir / "manifest.json.tmp"
        tmp.write_text(json.dumps({"entries": self.entries}, indent=2, ensure_ascii=False))
        tmp.replace(self.dir / "manifest.json")

    def record(self, entry, save_path=None):
        ident = _identity(entry)
        if ident in self.seen:
            return
        self._ensure()
        entry = dict(entry, restored=False)
        if save_path is not None and (Path(save_path).exists() or Path(save_path).is_symlink()):
            stored = self.dir / "files" / str(len(self.entries))
            copy_path(save_path, stored)
            entry["saved"] = str(stored.relative_to(self.dir))
        else:
            entry["saved"] = None
        self.entries.append(entry)
        self.seen.add(ident)
        self._save()


def _active(root):
    backups = []
    for manifest in sorted(root.glob("*/manifest.json")):
        data = json.loads(manifest.read_text())
        backups.append((manifest, data))
    return backups


def restore(theme_id, only=None, dry_run=False, out=print, cwd=None):
    """Restaura o estado anterior. Para cada item, vale o backup mais antigo ainda não restaurado."""
    root = state_dir(theme_id) / "backups"
    backups = _active(root)
    chosen = {}
    for b, (manifest, data) in enumerate(backups):
        for e, entry in enumerate(data["entries"]):
            if entry.get("restored") or (only and entry["target"] not in only):
                continue
            chosen.setdefault(_identity(entry), (b, e))
    if not chosen:
        out("Nada para restaurar.")
        return True

    ok = True
    notify = []
    for b, e in sorted(chosen.values(), reverse=True):
        manifest, data = backups[b]
        entry = data["entries"][e]
        out(f"  [{entry['target']}] {describe(entry)}")
        if dry_run:
            continue
        try:
            _restore_entry(entry, manifest.parent, cwd)
        except (OSError, subprocess.CalledProcessError) as err:
            out(f"    erro: {err}")
            ok = False
        notify += [n for n in entry.get("notify", []) if n not in notify]
    if dry_run:
        return ok
    _notify(notify)

    for manifest, data in backups:
        changed = False
        for entry in data["entries"]:
            if not entry.get("restored") and (not only or entry["target"] in only):
                entry["restored"] = True
                changed = True
        if changed:
            data["restored_at"] = datetime.now().isoformat(timespec="seconds")
            manifest.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return ok


def describe(entry):
    kind = entry["kind"]
    if kind == "file":
        what = "restaurar" if entry["existed"] else "remover"
        return f"{what} {entry['path']}"
    if kind == "block":
        return f"remover bloco de {entry['path']}"
    if kind == "key":
        group = "][".join(entry["group"])
        old = "(apagar chave)" if entry["old"] is None else repr(entry["old"])
        return f"{entry['file']} [{group}] {entry['key']} -> {old}"
    if kind == "registry":
        from .backends import registry
        return f"{registry.display(entry['key'])} {entry['name']} -> {registry.show(entry['old'])}"
    if kind == "font":
        what = "restaurar" if entry.get("saved") else "remover"
        return f"{what} fonte {entry['path']}"
    return f"{entry['name']} -> {entry['old'] or entry.get('default') or '(vazio)'}"


def _restore_entry(entry, bdir, cwd):
    _restore_one(entry, bdir, cwd)
    for d in entry.get("created_dirs", []):
        d = Path(d)
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()


def _restore_one(entry, bdir, cwd):
    kind = entry["kind"]
    saved = bdir / entry["saved"] if entry.get("saved") else None
    if kind == "file":
        path = Path(entry["path"])
        remove_path(path)
        if saved is not None:
            copy_path(saved, path)
    elif kind == "block":
        path = Path(entry["path"])
        begin, end = entry["markers"]
        if not path.exists():
            return
        text, newline = read_text_keep_newlines(path)
        cleaned = blocks.remove(text, begin, end)
        if saved is not None and cleaned.strip() == saved.read_text().strip():
            shutil.copy2(saved, path)
        elif saved is None and not cleaned.strip():
            path.unlink()
        else:
            write_text_newlines(path, cleaned, newline)
    elif kind == "key":
        kde.restore(entry["file"], entry["group"], entry["key"], entry["old"])
    elif kind == "registry":
        from .backends import registry
        registry.restore(entry["key"], entry["name"], entry["old"])
        registry.remove_empty_keys(entry.get("created_keys", []))
    elif kind == "font":
        _restore_font(entry, saved)
    elif kind == "state":
        value = entry["old"] or entry.get("default") or ""
        env = dict(os.environ, GIBI_VALUE=value)
        subprocess.run(entry["restore"], shell=True, check=True, env=env, cwd=cwd)


def _restore_font(entry, saved):
    from .backends import registry, winapi
    path = Path(entry["path"])
    winapi.remove_font(path)
    registry.restore(entry["key"], entry["name"], entry["old"])
    registry.remove_empty_keys(entry.get("created_keys", []))
    try:
        remove_path(path)
    except PermissionError:
        raise OSError(f"{path} está em uso por algum app; feche-o (ou faça logoff) e apague à mão") from None
    if saved is not None:
        copy_path(saved, path)
        winapi.add_font(path)


def _notify(areas):
    """Broadcasts recorded by the entries just restored (e.g. WM_SETTINGCHANGE after registry)."""
    if not areas or not platform.is_windows():
        return
    from .backends import winapi
    for area in areas:
        if area == "fonts":
            winapi.font_change()
        else:
            winapi.setting_change(area)

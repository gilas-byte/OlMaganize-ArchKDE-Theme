import filecmp
import hashlib
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

from . import blocks, kde, platform
from .backup import (BackupSession, copy_path, read_text_keep_newlines, remove_path, state_dir,
                     write_text_newlines)
from .render import RenderError, render_text, render_tree

MODES = ("symlink", "copy", "managed-block")


class TargetError(Exception):
    pass


class Target:
    def __init__(self, path):
        self.dir = Path(path)
        with open(self.dir / "target.toml", "rb") as f:
            raw = tomllib.load(f)
        try:
            self.platforms = platform.platforms_of(raw)
        except ValueError as err:
            raise TargetError(f"{self.dir.name}: {err}") from None
        # The [windows] table (if any) replaces top-level keys when running on Windows.
        self.meta = platform.overlay(raw)
        self.name = self.meta.get("name", self.dir.name)
        self.order = self.meta.get("order", 50)
        self.hidden = self.dir.name.startswith("_")

    @property
    def description(self):
        return self.meta.get("description", "")

    @property
    def supported(self):
        return platform.current() in self.platforms

    def packages(self):
        return list(self.meta.get("packages", [])), list(self.meta.get("aur_packages", []))


def load_targets(root):
    targets = [Target(p) for p in sorted((Path(root) / "targets").iterdir()) if (p / "target.toml").is_file()]
    return sorted(targets, key=lambda t: (t.order, t.name))


def select(targets, only):
    """Targets to run. Without --only, targets of other platforms are left out silently;
    with --only they stay and run() reports them as skipped."""
    if not only:
        return [t for t in targets if not t.hidden and t.supported]
    by_name = {t.name: t for t in targets}
    unknown = [n for n in only if n not in by_name]
    if unknown:
        raise TargetError(f"alvo(s) desconhecido(s): {', '.join(unknown)}")
    return [t for t in targets if t.name in only]


def missing_packages(names):
    # Windows: no target needs packages yet (winget support comes with the first one that does).
    if not names or platform.is_windows():
        return []
    result = subprocess.run(["pacman", "-T", *names], capture_output=True, text=True)
    return result.stdout.split()


def aur_helper():
    return next((h for h in ("paru", "yay") if shutil.which(h)), None)


def _same(a, b, ignore=()):
    """Conteúdo igual? `ignore`: nomes que o app cria no destino e não contam."""
    a, b = Path(a), Path(b)
    if b.is_symlink() or not b.exists():
        return False
    if a.is_file():
        return b.is_file() and filecmp.cmp(a, b, shallow=False)
    cmp = filecmp.dircmp(a, b, ignore=filecmp.DEFAULT_IGNORES + list(ignore))

    def equal(c):
        if c.left_only or c.right_only or c.funny_files:
            return False
        _, mismatch, errors = filecmp.cmpfiles(c.left, c.right, c.common_files, shallow=False)
        return not mismatch and not errors and all(equal(s) for s in c.subdirs.values())

    return equal(cmp)


def _missing_dirs(path):
    missing = []
    parent = Path(path).parent
    while not parent.exists():
        missing.append(str(parent))
        parent = parent.parent
    return missing


def replace_font_family(current, family):
    if not current:
        return f"{family},10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
    parts = current.split(",")
    parts[0] = family
    return ",".join(parts)


class Runner:
    def __init__(self, root, palette, dry_run=False, out=print):
        self.root = Path(root)
        self.palette = palette
        self.tokens = palette.tokens()
        self.tokens.update(platform.tokens(palette.id))
        self.dry_run = dry_run
        self.out = out
        self.build = self.root / "build"
        self.session = BackupSession(palette.id)

    def t(self, value, origin):
        if isinstance(value, bool):
            return "true" if value else "false"
        return render_text(str(value), self.tokens, origin)

    def sh(self, cmd, value=None, capture=False):
        env = dict(os.environ)
        if value is not None:
            env["GIBI_VALUE"] = value
        result = subprocess.run(
            cmd, shell=True, cwd=self.root, env=env, text=True,
            capture_output=capture, check=not capture,
        )
        return result

    # --- render / detecção / dependências -------------------------------------------------

    def render(self, target):
        # "generate": script que (re)escreve templates/ a partir da paleta antes do render
        # (ex.: o SVG do Kvantum, cuja geometria depende de raios e profundidades).
        # Deve ser determinístico e só gravar o que mudou.
        generator = target.meta.get("generate")
        if generator:
            result = subprocess.run([sys.executable, str(target.dir / generator)], cwd=self.root,
                                    capture_output=True, text=True)
            if result.returncode != 0:
                raise TargetError(f"generate falhou: {result.stderr.strip()}")
        templates = target.dir / "templates"
        if templates.is_dir():
            render_tree(templates, self.build / target.name, self.tokens)

    def detect(self, target):
        # detect_paths: detected if any of these exists (no shell; the way Windows targets detect).
        paths = target.meta.get("detect_paths")
        if paths:
            return any(Path(platform.expand(self.t(p, f"{target.name}: detect_paths"))).exists()
                       for p in paths)
        cmd = target.meta.get("detect")
        if not cmd:
            return True
        return self.sh(cmd, capture=True).returncode == 0

    def ensure_packages(self, target):
        repo, aur = target.packages()
        missing = missing_packages(repo + aur)
        if not missing:
            return True
        repo_missing = [p for p in missing if p in repo]
        aur_missing = [p for p in missing if p not in repo]
        self.out(f"  pacotes faltando: {', '.join(missing)}")
        if self.dry_run:
            self.out("  (dry-run) instalaria os pacotes acima e seguiria")
            return True
        if not sys.stdin.isatty():
            self.out("  sem terminal interativo para confirmar a instalação")
            return False
        answer = input(f"  Instalar {', '.join(missing)}? [s/N] ").strip().lower()
        if answer not in ("s", "sim", "y", "yes"):
            return False
        if repo_missing:
            subprocess.run(["sudo", "pacman", "-S", "--needed", *repo_missing], check=True)
        if aur_missing:
            helper = aur_helper()
            if helper is None:
                self.out("  nenhum helper do AUR (paru/yay) encontrado")
                return False
            subprocess.run([helper, "-S", "--needed", *aur_missing], check=True)
        return not missing_packages(repo + aur)

    # --- aplicação ------------------------------------------------------------------------

    # --- conteúdo renderizado ------------------------------------------------------------
    # Um symlink para build/ não muda quando só o conteúdo renderizado muda (ex.: nova cor na
    # paleta). Para os posts e o reapply_on_change enxergarem isso, guardamos o hash do
    # build/<alvo> aplicado em ~/.local/state/<id>/rendered/.

    def _fingerprint_path(self, target):
        return state_dir(self.palette.id) / "rendered" / f"{target.name}.sha256"

    def _fingerprint(self, target):
        root = self.build / target.name
        if not root.is_dir():
            return None
        digest = hashlib.sha256()
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            digest.update(path.relative_to(root).as_posix().encode() + b"\0" + path.read_bytes())
        return digest.hexdigest()

    @staticmethod
    def _mode(spec):
        # Symlinks on Windows need admin or developer mode: copy instead (PHASE-WindowsOnly.md §6).
        # Content changes are then caught by comparing the copy with build/.
        mode = spec.get("mode", "symlink")
        return "copy" if mode == "symlink" and platform.is_windows() else mode

    def _render_changed(self, target):
        """Hash atual se o conteúdo mudou desde o último apply de um alvo com symlink, senão None."""
        if not any(self._mode(spec) == "symlink" for spec in target.meta.get("files", [])):
            return None
        current = self._fingerprint(target)
        path = self._fingerprint_path(target)
        stored = path.read_text().strip() if path.is_file() else None
        return current if current and current != stored else None

    def apply(self, target):
        """Aplica um alvo. Retorna a lista de mudanças (descrições)."""
        changes = []
        files_changed = False
        rendered = self._render_changed(target)
        for spec in target.meta.get("files", []):
            if self._file(target, spec, changes):
                files_changed = True
        if rendered and not files_changed:
            changes.append(f"conteúdo renderizado atualizado (build/{target.name})")
            files_changed = True
        for spec in target.meta.get("fonts", []):
            if self._fonts(target, spec, changes):
                files_changed = True
        for spec in target.meta.get("keys", []):
            self._key(target, spec, changes)
        for spec in target.meta.get("registry", []):
            self._registry(target, spec, changes)
        for spec in target.meta.get("states", []):
            self._state(target, spec, changes, files_changed)
        if changes:
            for spec in target.meta.get("post", []):
                if "notify" in spec:
                    changes.append(f"avisar o Windows: {spec['notify']}")
                    if not self.dry_run:
                        self._notify(spec["notify"])
                    continue
                cmd = self.t(spec["cmd"], f"{target.name}: post")
                changes.append(f"executar: {cmd}")
                if not self.dry_run:
                    self.sh(cmd)
        if rendered and not self.dry_run:
            path = self._fingerprint_path(target)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(rendered + "\n")
        return changes

    def _file(self, target, spec, changes):
        mode = self._mode(spec)
        if mode not in MODES:
            raise TargetError(f"modo inválido: {mode}")
        src = Path(spec["src"])
        if src.parts[0] != "templates":
            raise TargetError(f"src deve ficar em templates/: {src}")
        built = self.build / target.name / Path(*src.parts[1:])
        if not built.exists():
            raise TargetError(f"arquivo renderizado não existe: {built}")
        dest = Path(platform.expand(self.t(spec["dest"], f"{target.name}: dest")))
        exists = dest.exists() or dest.is_symlink()

        if mode == "symlink":
            if dest.is_symlink() and os.readlink(dest) == str(built):
                return False
            changes.append(f"symlink {dest} -> {built}")
            if not self.dry_run:
                self._record_file(target, dest, exists)
                remove_path(dest)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.symlink_to(built)
            return True

        if mode == "copy":
            if _same(built, dest, spec.get("ignore", [])):
                return False
            changes.append(f"copiar {built} -> {dest}")
            if not self.dry_run:
                self._record_file(target, dest, exists)
                remove_path(dest)
                copy_path(built, dest)
            return True

        begin, end = blocks.markers(self.palette.id, spec.get("comment", "#"))
        current, newline = read_text_keep_newlines(dest) if dest.is_file() else ("", None)
        new = blocks.upsert(current, built.read_text(), begin, end, spec.get("position", "bottom"))
        # Só a quebra de linha final não conta: o gtkconfig do KDE reescreve o gtk.css sem
        # ela ao aplicar o Look-and-Feel, e o bloco continua intacto.
        if new.rstrip("\n") == current.rstrip("\n"):
            return False
        changes.append(f"bloco gerenciado em {dest}")
        if not self.dry_run:
            entry = {"kind": "block", "target": target.name, "path": str(dest), "markers": [begin, end],
                     "created_dirs": _missing_dirs(dest), **self._notify_field(target)}
            self.session.record(entry, save_path=dest if exists else None)
            dest.parent.mkdir(parents=True, exist_ok=True)
            write_text_newlines(dest, new, newline)
        return True

    def _record_file(self, target, dest, existed):
        entry = {"kind": "file", "target": target.name, "path": str(dest), "existed": existed,
                 "created_dirs": _missing_dirs(dest), **self._notify_field(target)}
        self.session.record(entry, save_path=dest if existed else None)

    def _key(self, target, spec, changes):
        origin = f"{target.name}: key {spec.get('key')}"
        file = self.t(spec["file"], origin)
        if file.startswith("~"):
            file = os.path.expanduser(file)
        group = spec["group"]
        group = [self.t(g, origin) for g in ([group] if isinstance(group, str) else group)]
        key = spec["key"]
        current = kde.read(file, group, key)
        if spec.get("delete"):
            desired = None
        elif spec.get("transform") == "font-family":
            desired = replace_font_family(current, self.t(spec["value"], origin))
        elif "transform" in spec:
            raise TargetError(f"transform desconhecido: {spec['transform']}")
        else:
            desired = self.t(spec["value"], origin)
        if current == desired:
            return
        shown = "(apagar)" if desired is None else repr(desired)
        changes.append(f"{file} [{']['.join(group)}] {key} = {shown}")
        if self.dry_run:
            return
        self.session.record({"kind": "key", "target": target.name, "file": file,
                             "group": group, "key": key, "old": current})
        kde.restore(file, group, key, desired)

    # --- Windows: registro, fontes, avisos ------------------------------------------------

    def _notify_areas(self, target):
        return [spec["notify"] for spec in target.meta.get("post", []) if "notify" in spec]

    def _notify_field(self, target):
        """{"notify": [...]} for a manifest entry, so restore repeats the target's notices.
        Empty (no key at all) for targets without them, which keeps Linux manifests as before."""
        areas = self._notify_areas(target)
        return {"notify": areas} if areas else {}

    @staticmethod
    def _notify(area):
        from .backends import winapi
        winapi.notify(area)

    def _registry(self, target, spec, changes):
        from .backends import registry
        origin = f"{target.name}: registry {spec.get('name')}"
        try:
            sub = registry.split(self.t(spec["key"], origin))
            name = self.t(spec["name"], origin)
            want = None if spec.get("delete") else registry.desired(spec, self.t(spec["value"], origin))
        except (registry.RegistryError, ValueError) as err:
            raise TargetError(f"{origin}: {err}") from None
        current = registry.read(sub, name)
        if current == want:
            return
        changes.append(f"{registry.display(sub)} {name} = {registry.show(want)}")
        if self.dry_run:
            return
        self.session.record({"kind": "registry", "target": target.name, "key": sub, "name": name,
                             "old": current, "created_keys": registry.missing_keys(sub),
                             "notify": self._notify_areas(target)})
        registry.restore(sub, name, want)

    def _fonts(self, target, spec, changes):
        """Install the font files of one [[fonts]] entry for the current user."""
        from .backends import fonts, registry, winapi
        origin = f"{target.name}: fonts"
        family = self.t(spec["family"], origin)
        source = self.t(spec["source"], origin)
        sha256 = spec["sha256"].lower()
        pattern = spec["files"]
        archive = fonts.locate(self.palette.id, source, sha256, target.dir)
        if archive is None:
            if self.dry_run:
                changes.append(f"baixar {source} e instalar a fonte {family} ({pattern}) por usuário")
                return True
            try:
                archive = fonts.fetch(self.palette.id, source, sha256)
            except fonts.FontError as err:
                raise TargetError(f"{origin}: {err}") from None
            changes.append(f"baixado {source}")
        try:
            files = fonts.members(archive, pattern)
            key = registry.split(fonts.FONTS_KEY)
        except (fonts.FontError, registry.RegistryError, OSError) as err:
            raise TargetError(f"{origin}: {err}") from None
        changed = False
        for filename, data in files:
            try:
                value = fonts.value_name(data)
            except fonts.FontError as err:
                raise TargetError(f"{origin}: {filename}: {err}") from None
            if fonts.machine_has(value):
                continue  # already installed for every user
            dest = fonts.fonts_dir() / filename
            want = {"type": "string", "data": str(dest)}
            current = registry.read(key, value)
            if current == want and fonts.same_file(dest, data):
                continue
            changes.append(f"fonte {family}: {dest}")
            changed = True
            if self.dry_run:
                continue
            existed = dest.exists()
            self.session.record({"kind": "font", "target": target.name, "path": str(dest),
                                 "key": key, "name": value, "old": current,
                                 "created_keys": registry.missing_keys(key),
                                 "created_dirs": _missing_dirs(dest), "notify": ["fonts"]},
                                save_path=dest if existed else None)
            if existed:
                winapi.remove_font(dest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            registry.write(key, value, want)
            winapi.add_font(dest)
        if changed and not self.dry_run:
            winapi.font_change()
        return changed

    def _state(self, target, spec, changes, files_changed):
        origin = f"{target.name}: state {spec['name']}"
        value = self.t(spec["value"], origin)
        get = self.sh(self.t(spec["get"], origin), capture=True)
        if get.returncode != 0:
            raise TargetError(f"{origin}: comando get falhou: {get.stderr.strip()}")
        current = get.stdout.strip()
        reapply = spec.get("reapply_on_change", False) and files_changed
        if current == value and not reapply:
            return
        set_cmd = self.t(spec["set"], origin)
        changes.append(f"{spec['name']}: {current or '(vazio)'} -> {value}")
        if self.dry_run:
            return
        if current != value:
            self.session.record({
                "kind": "state", "target": target.name, "name": spec["name"], "old": current,
                "default": self.t(spec.get("default", ""), origin),
                "restore": self.t(spec.get("restore", spec["set"]), origin),
            })
        self.sh(set_cmd, value=value)


def run(root, palette, targets, dry_run=False, out=print):
    runner = Runner(root, palette, dry_run=dry_run, out=out)
    summary = []
    for target in targets:
        out(f"\n==> {target.name} — {target.description}")
        if not target.supported:
            where = ", ".join(target.platforms)
            out(f"  só para {where}, pulando")
            summary.append((target.name, f"pulado (só {where})"))
            continue
        try:
            if not runner.detect(target):
                out("  não detectado, pulando")
                summary.append((target.name, "pulado (não detectado)"))
                continue
            if not runner.ensure_packages(target):
                summary.append((target.name, "pulado (dependências faltando)"))
                continue
            runner.render(target)
            changes = runner.apply(target)
        except (RenderError, TargetError, OSError, subprocess.CalledProcessError) as err:
            out(f"  erro: {err}")
            summary.append((target.name, f"erro: {err}"))
            continue
        for change in changes:
            out(f"  {'~' if dry_run else '+'} {change}")
        message = target.meta.get("message")
        if changes and message:
            out("")
            for line in runner.t(message, f"{target.name}: message").rstrip().splitlines():
                out(f"  {line}")
        if not changes:
            out("  sem mudanças")
        verb = "mudaria" if dry_run else "aplicado"
        summary.append((target.name, f"{verb} ({len(changes)} mudança(s))" if changes else "sem mudanças"))

    out("\nResumo:")
    width = max((len(n) for n, _ in summary), default=0)
    for name, status in summary:
        out(f"  {name:<{width}}  {status}")
    if runner.session.dir:
        out(f"\nBackup: {runner.session.dir}")
    return all(not s.startswith("erro") for _, s in summary)

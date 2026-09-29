# Equivalente ao papirus-folders, mas como tema derivado em ~/.local/share/icons (sem sudo).
import configparser
import os
import re
import shutil
from pathlib import Path

MARKER = ".gibi-generated"
# Versão do formato do tema gerado. Mudou o que build() escreve? Suba o número: current()
# passa a responder "" para temas antigos e o alvo icons regenera no próximo install.
# 2: copia FollowsColorScheme do tema base.
# 3: recria os apelidos (ex.: inode-directory -> folder.svg) apontando para a cor escolhida.
FORMAT = "3"


def _data_home():
    return Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share")


def _base_dir(base):
    for root in (_data_home() / "icons", Path("/usr/share/icons")):
        if (root / base / "index.theme").is_file():
            return root / base
    raise FileNotFoundError(f"tema de ícones base não encontrado: {base}")


def theme_dir(name):
    return _data_home() / "icons" / name


def current(name):
    """Cor das pastas do tema gerado, ou "" se não existe ou foi gerado num formato antigo."""
    marker = theme_dir(name) / MARKER
    if not marker.is_file():
        return ""
    color, _, version = marker.read_text().strip().partition("\n")
    return color if version.strip() == FORMAT else ""


def remove(name):
    path = theme_dir(name)
    if (path / MARKER).is_file():
        shutil.rmtree(path)
        if not any(path.parent.iterdir()):
            path.parent.rmdir()


def _aliases(base_dir, places, links):
    """Apelidos do tema base que acabam num ícone trocado.

    No Papirus, nomes como inode-directory (o ícone de pasta do Dolphin) são symlinks
    relativos para folder.svg. Sem recriá-los aqui, eles resolvem dentro do tema base e a
    pasta aparece na cor padrão.
    """
    out = {}
    for d in places:
        replaced = {filename for dd, filename in links if dd == d}
        folder = base_dir / d
        for entry in folder.iterdir():
            if entry.name in replaced or not entry.is_symlink():
                continue
            target, seen = entry.name, set()
            while (folder / target).is_symlink():
                target = os.readlink(folder / target)
                if "/" in target or target in seen:
                    break
                seen.add(target)
                if target in replaced:
                    out[(d, entry.name)] = links[(d, target)]
                    break
    return out


def build(name, base, color):
    base_dir = _base_dir(base)
    index = configparser.ConfigParser(interpolation=None, strict=False)
    index.optionxform = str
    index.read(base_dir / "index.theme")
    theme = index["Icon Theme"]
    dirs = [d for key in ("Directories", "ScaledDirectories") for d in theme.get(key, "").split(",")]
    places = [d for d in dirs if d.endswith("/places") and "symbolic" not in d and (base_dir / d).is_dir()]

    folder_re = re.compile(rf"^folder-{re.escape(color)}(-.+)?\.svg$")
    user_re = re.compile(rf"^user-{re.escape(color)}-(.+)\.svg$")
    links = {}
    for d in places:
        for icon in (base_dir / d).iterdir():
            if m := folder_re.match(icon.name):
                links[(d, f"folder{m.group(1) or ''}.svg")] = icon
            elif m := user_re.match(icon.name):
                links[(d, f"user-{m.group(1)}.svg")] = icon
    if not links:
        raise ValueError(f"cor de pasta '{color}' não existe em {base}")
    links.update(_aliases(base_dir, places, links))

    remove(name)
    out = theme_dir(name)
    if out.exists():
        raise FileExistsError(f"{out} existe e não foi gerado pelo gibi")
    used = sorted({d for d, _ in links})
    for (d, filename), icon in links.items():
        (out / d).mkdir(parents=True, exist_ok=True)
        (out / d / filename).symlink_to(icon)

    lines = [
        "[Icon Theme]",
        f"Name={name}",
        f"Comment={base} com pastas {color} (gerado pelo gibi)",
        f"Inherits={base},{theme.get('Inherits', 'hicolor')}",
        # Sem esta flag o Plasma não recolore os ícones symbolic, e os do Papirus-Dark
        # (os mesmos arquivos do Papirus claro, em #444444) aparecem quase pretos.
        f"FollowsColorScheme={theme.get('FollowsColorScheme', 'false')}",
        "Directories=" + ",".join(d for d in used if "@" not in d),
        "ScaledDirectories=" + ",".join(d for d in used if "@" in d),
        "",
    ]
    for d in used:
        lines.append(f"[{d}]")
        lines += [f"{k}={v}" for k, v in index[d].items()]
        lines.append("")
    (out / "index.theme").write_text("\n".join(lines))
    (out / MARKER).write_text(f"{color}\n{FORMAT}\n")

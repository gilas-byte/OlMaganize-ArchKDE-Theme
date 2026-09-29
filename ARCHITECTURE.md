# Tema retro-moderno para Arch + KDE — Arquitetura

> Documento compartilhado pelas duas fases. Leia inteiro antes de executar `PHASE-1.md` ou `PHASE-2.md`.
> Nome do tema ainda não foi decidido. Use o codinome provisório **`gibi`** e mantenha o nome definido em **um único lugar** (`palette.toml → [theme].id` / `[theme].name`), para que renomear depois seja trivial.

## 1. Objetivo e escopo

Um tema pessoal para **Arch Linux / CachyOS com KDE Plasma 6**, que reproduz no sistema inteiro a sensação do tema **Primary** do Obsidian (por Cecilia May): marrons quentes, texto bege de baixo contraste, sensação de "revista antiga", botões com efeito de **tecla/botão de videogame**, e um acento amarelo vivo.

- Uso: pessoal, em várias máquinas do mesmo usuário, todas Arch + KDE.
- Instalação: clonar o repo e rodar um comando. Mesmo resultado em qualquer máquina, **sem perfis** por hardware.
- Tem que ser reversível: `uninstall` volta ao estado anterior.

Crédito obrigatório: o topo do `README.md` deve creditar o tema **Primary for Obsidian** de Cecilia May (https://github.com/primary-theme/obsidian) como inspiração e fonte da paleta base. Nenhum código do Primary é copiado; só valores de cor.

Licença do repo: **GPL-3.0**.

## 2. Stack

| Camada | Escolha | Motivo |
|---|---|---|
| Entrada do usuário | `install.sh` / `uninstall.sh` em **bash** | Ponto de entrada familiar no Arch |
| Lógica (render, aplicar, backup) | **Python 3, só stdlib** (`tomllib`, `string.Template`, `pathlib`, `shutil`, `subprocess`, `argparse`) | Python já vem no Arch; parsear TOML e manipular arquivos em bash é frágil |
| Fonte da verdade | `palette.toml` | Uma paleta alimenta todos os apps |
| Templates | arquivos com placeholders `${token}` | Funciona para qualquer formato de texto, inclusive SVG (fase 2) |
| Aplicação no KDE | `plasma-apply-colorscheme`, `kwriteconfig6`, `plasma-apply-lookandfeel` | APIs oficiais do Plasma 6 |
| Dependências | `pacman` e, se necessário, `paru` (AUR) | Padrão Arch/CachyOS |

Os scripts bash são finos: checam pré-requisitos e chamam `python3 -m tooling ...`.

## 3. Paleta

### 3.1 Base (marrons quentes, derivados do Primary dark)

| Token | Hex | Papel |
|---|---|---|
| `base.140` | `#1C1712` | fundo mais profundo, texto sobre amarelo |
| `base.120` | `#26211C` | botões em repouso, fundo de campos |
| `base.110` | `#2A241E` | fundo secundário (sidebars, painéis) |
| `base.100` | `#2E261F` | **fundo principal de janela** |
| `base.90` | `#342C23` | superfícies elevadas (cards, popups) |
| `base.80` | `#3B3026` | bordas, hover |
| `base.70` | `#51402F` | bordas fortes, separadores |
| `base.60` | `#6B563D` | texto desabilitado |
| `base.50` | `#917959` | texto apagado (faint) |
| `base.40` | `#AB916D` | texto secundário (muted), itens de sidebar |
| `base.20` | `#D7C0A3` | **texto normal** |
| `base.10` | `#EBDAC6` | texto forte, títulos, texto selecionado |

### 3.2 Acentos

| Token | Hex | Papel |
|---|---|---|
| `accent.primary` | `#FFEA00` | **ação / foco**: botão principal, aba ativa, anel de foco, cursor do terminal |
| `accent.on_primary` | `#1C1712` | texto/ícone sobre o amarelo (sempre) |
| `accent.secondary` | `#A58BC0` | **seleção / referência**: texto selecionado, tags, links visitados, ANSI magenta |
| `selection.bg` | `#5E4E5F` | fundo sólido de seleção (roxo a ~40% sobre `base.100`) |
| `selection.bg_subtle` | `#4F424C` | seleção inativa / hover de seleção (~28%) |
| `selection.fg` | `#EBDAC6` | texto sobre seleção |

### 3.3 Semânticas e ANSI (cores primárias "envelhecidas" do Primary dark)

| Token | Hex |
|---|---|
| `sem.red` | `#E4574E` |
| `sem.orange` | `#EEA359` |
| `sem.yellow` | `#F9CF51` |
| `sem.green` | `#64C271` |
| `sem.cyan` | `#5BAFB7` |
| `sem.blue` | `#639CC0` |
| `sem.pink` | `#E06C8A` |

Uso: erro = red, aviso = orange, sucesso = green, informação = blue. O `sem.yellow` é o amarelo "de conteúdo" (ex.: ANSI yellow); **não confundir** com `accent.primary`.

### 3.4 Regras de uso das cores (restrições de design, obrigatórias)

1. **Amarelo `#FFEA00` nunca vira fundo de área maior que um botão.** Nada de barras, painéis ou abas inteiras amarelas. Ele é pontual: borda, anel, preenchimento de botão principal, cursor.
2. Texto sobre amarelo é sempre `accent.on_primary`.
3. Roxo é tempero (~5% da tela). Só nos papéis listados em 3.2.
4. Hierarquia visual: marrons ~60%, bege (texto) ~30%, amarelo ~5-10%, roxo ~5%.
5. Todo par texto/fundo de texto corrido deve passar **WCAG AA (4.5:1)**, exceto os tokens explicitamente "apagados" (`base.50`, `base.60`), que só precisam de 3:1. O renderizador verifica isso (ver 5.3).

### 3.5 Tokens de forma (usados no GTK e principalmente na fase 2)

| Token | Valor | Uso |
|---|---|---|
| `shape.radius_s` | `4` px | checkbox, chips |
| `shape.radius_m` | `7` px | botões, campos, itens de lista |
| `shape.radius_l` | `10` px | cards, menus, janelas (se aplicável) |
| `shape.border_width` | `1` px | borda interna escura |
| `shape.border_color` | `rgba(0,0,0,0.30)` | borda interna de botões/campos |
| `keycap.highlight` | `rgba(255,255,255,0.10)` | linha de brilho de 1px no topo do botão |
| `keycap.base_depth` | `3` px | altura da "base" escura interna na parte de baixo |
| `keycap.base_color` | `rgba(0,0,0,0.28)` | cor dessa base |
| `keycap.drop` | `0 2px 3px rgba(0,0,0,0.30)` | sombra externa curtinha |
| `surface.float_opacity` | `0.88` | opacidade de superfícies flutuantes (painel, menus, notificações) |
| `surface.blur` | leve | blur só em superfícies flutuantes, nunca em janelas |

Efeito de tecla, em estados: **repouso** = brilho no topo + borda interna + base inferior + drop; **hover** = fundo um passo mais claro (`base.90` → `base.80`); **pressionado** = sem base inferior e sem drop, conteúdo desce 1px (sensação de tecla apertada); **foco** = anel de 2px em `accent.primary` a ~45% de opacidade; **desabilitado** = sem sombras, opacidade 0.3.

### 3.6 Tipografia

- Interface: **Inter** (pacote `inter-font`).
- Monoespaçada / terminal: **CaskaydiaCove Nerd Font** (pacote `ttf-cascadia-code-nerd`), por causa dos ícones em prompt/fastfetch.

## 4. Estrutura do repositório

```
gibi/
├── README.md                 # créditos à Cecilia May no topo, instalação, screenshots
├── LICENSE                   # GPL-3.0
├── ARCHITECTURE.md           # este arquivo
├── PHASE-1.md
├── PHASE-2.md
├── palette.toml              # fonte única da verdade (cores + forma + tipografia + nome)
├── install.sh                # entrada: checa deps, chama python3 -m tooling apply
├── uninstall.sh              # entrada: chama python3 -m tooling restore
├── tooling/                  # Python stdlib apenas
│   ├── __main__.py           # CLI: render | apply | restore | check
│   ├── palette.py            # carrega palette.toml, gera variantes de formato
│   ├── render.py             # renderiza templates/ → build/
│   ├── contrast.py           # verificação WCAG
│   ├── targets.py            # registro e execução dos alvos
│   └── backup.py             # backup/restauração com timestamp
├── targets/                  # um diretório por alvo
│   └── <alvo>/
│       ├── target.toml       # metadados: deps, arquivos, modo de aplicação, comandos pós
│       └── templates/        # arquivos com ${token}
└── build/                    # saída renderizada (no .gitignore)
```

### 4.1 Contrato do `palette.toml`

```toml
[theme]
id = "gibi"          # slug usado em nomes de arquivo
name = "Gibi"        # nome exibido

[base]
"140" = "#1C1712"
# ... demais tons

[accent]
primary = "#FFEA00"
on_primary = "#1C1712"
secondary = "#A58BC0"

[selection]
bg = "#5E4E5F"
bg_subtle = "#4F424C"
fg = "#EBDAC6"

[sem]
red = "#E4574E"
# ...

[shape]
radius_s = 4
# ...

[keycap]
# ...

[font]
ui = "Inter"
mono = "CaskaydiaCove Nerd Font"
```

### 4.2 Contrato dos templates

- Placeholders `${secao_chave}` achatados com `_` (ex.: `${accent_primary}`, `${base_100}`).
- Para cada cor, o renderizador expõe variantes: `${x}` = `#RRGGBB`, `${x_nohash}` = `RRGGBB`, `${x_rgb}` = `R,G,B`, `${x_r}`/`${x_g}`/`${x_b}` separados. Isso cobre `.colors` do KDE (`R,G,B`), CSS, Ghostty, manifest do Brave (`[R, G, B]`) e SVG.
- Tokens numéricos e de texto (forma, fonte, id do tema) também ficam disponíveis.
- Placeholder desconhecido = **erro de render** (usar `Template.substitute`, nunca `safe_substitute`). Isso evita arquivo meio renderizado passando despercebido.
- O renderizador trata qualquer arquivo de texto igual, incluindo `.svg` e `.kvconfig` (necessário na fase 2).

### 4.3 Contrato do `target.toml`

```toml
name = "ghostty"
description = "Terminal Ghostty"
packages = ["ghostty"]            # checados; instalados só com confirmação
aur_packages = []
detect = "command -v ghostty"     # se falhar, alvo é pulado com aviso (não é erro)

[[files]]
src = "templates/gibi"            # relativo ao alvo, renderizado em build/
dest = "~/.config/ghostty/themes/${theme_id}"
mode = "symlink"                  # symlink | copy | managed-block | kwrite

[[post]]
cmd = "..."                       # comandos após aplicar (opcional)
```

Modos:
- `symlink`: arquivo inteiramente do tema. Padrão.
- `copy`: quando o app não segue symlink ou reescreve o arquivo.
- `managed-block`: insere/atualiza um bloco delimitado por `# >>> gibi >>>` / `# <<< gibi <<<` dentro de um arquivo do usuário, sem tocar no resto (ex.: linha `theme =` do Ghostty, `@import` em `gtk.css`).
- `kwrite`: chaves aplicadas com `kwriteconfig6 --file X --group Y --key Z value`. **Obrigatório para arquivos que o próprio KDE reescreve** (`kdeglobals`, `kwinrc`, `klassyrc`, `plasmarc` etc.). Nunca criar symlink nesses arquivos.

## 5. Comportamento do instalador

### 5.1 Comandos

```
./install.sh                 # render + check + apply de todos os alvos detectados
./install.sh --only ghostty  # um alvo
./install.sh --dry-run       # mostra o que faria, não altera nada
./install.sh --list          # lista alvos e se foram detectados
./uninstall.sh               # restaura o último backup e volta ao Breeze
```

### 5.2 Regras

1. **Idempotente**: rodar duas vezes seguidas não gera mudanças na segunda.
2. **Backup antes de tocar**: qualquer arquivo existente (ou valor antigo de `kwriteconfig6`) é salvo em `~/.local/state/gibi/backups/<timestamp>/` com um `manifest.json` do que foi alterado.
3. `uninstall` usa esse manifest para restaurar; para chaves KDE, restaura o valor antigo (ou apaga a chave, se não existia).
4. Nunca usar `sudo` para arquivos do tema. Tudo vai para `~`. `sudo` só aparece no `pacman -S`, com confirmação.
5. Alvo não detectado (app não instalado) = pulado com aviso, não erro.
6. Saída clara no terminal: um resumo por alvo (aplicado / pulado / erro).

### 5.3 Verificação de contraste

`python3 -m tooling check` calcula a razão de contraste WCAG dos pares definidos (texto × fundo) e **falha o install** se algum par obrigatório ficar abaixo do mínimo da seção 3.4. Pares mínimos: `base.20`/`base.100`, `base.10`/`base.100`, `base.40`/`base.100`, `base.20`/`base.110`, `accent.on_primary`/`accent.primary`, `selection.fg`/`selection.bg`.

## 6. Decisões e porquês

- **Paleta estática, não Matugen**: o tema tem identidade fixa. Gerar paleta a partir de wallpaper distorceria as cores escolhidas.
- **Blur meio-termo**: janelas opacas (sensação de papel), blur leve só em painel, menus, lançador e notificações. Também reduz problema de composição em máquinas com GPU híbrida.
- **Klassy como decoração de janela e estilo de widgets na fase 1**; **Kvantum assume os widgets na fase 2** para o efeito de tecla. Klassy continua como decoração de janela.
- **Sombras de janela difusas** (Klassy), não sombra dura deslocada. A sombra "de tecla" existe só nos widgets.
- **Sem perfis desktop/notebook**: um instalador para todas as máquinas.
- **Python stdlib**: zero dependências extras além do que o Arch já tem.

## 7. Fora de escopo (por agora)

- Decoração de janela própria em SVG (Aurorae).
- Tema dinâmico baseado em wallpaper (estilo Matugen).
- Pacote no AUR.
- Suporte a outros sistemas (Windows/macOS) ou outros DEs (GNOME, Hyprland).
- Tema claro.
- **Obsidian**: continua com o tema Primary original, sem snippet nem alteração. Ele é a referência visual do projeto, não um alvo.
- Alvos da lista "depois": btop, fastfetch, starship, VS Code, Vesktop, Spicetify, cursor, SDDM, splash. A estrutura de `targets/` deve tornar cada um deles "só mais uma pasta".
- ~~Plasma Style próprio~~: implícito como fora de escopo nas fases 1 e 2, entrou na fase 3 (`PHASE-3.md`).

## 8. Verificação visual

O Claude Code não vê a tela. Ao final de cada fase, gerar um `docs/CHECKLIST-FASE-N.md` com o que o usuário deve conferir visualmente (apps a abrir, estados a testar) e o comando para screenshot: `spectacle -b -f -n -o ~/gibi-check-<app>.png`.

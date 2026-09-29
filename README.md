# Gibi

> **Créditos:** a paleta e a sensação visual deste tema vêm do **[Primary for Obsidian](https://github.com/primary-theme/obsidian)**, de **Cecilia May**. Ele serviu de inspiração e é a fonte da paleta base. Nenhum código do Primary foi copiado, só os valores de cor.

Tema retro-moderno para **Arch Linux / CachyOS com KDE Plasma 6**: marrons quentes, texto bege de baixo contraste, sensação de revista antiga e um acento amarelo vivo usado com parcimônia. "Gibi" é um codinome provisório. O nome fica em um único lugar (`palette.toml → [theme]`), então renomear é trocar `id`/`name` lá e rodar `./install.sh` de novo.

## Instalação

```sh
git clone <repo> ~/Documents/gibi-theme && cd ~/Documents/gibi-theme
./install.sh --dry-run       # mostra o que faria, sem alterar nada
./install.sh                 # render + checagem de contraste + aplica todos os alvos detectados
```

Depois do primeiro install, faça **logout/login** uma vez e siga `docs/CHECKLIST-FASE-1.md`.

```sh
./install.sh --only ghostty  # só um alvo (ou vários: --only gtk,ghostty)
./install.sh --list          # lista os alvos, se foram detectados e dependências faltando
./uninstall.sh               # restaura arquivos e chaves do KDE ao estado anterior
./uninstall.sh --dry-run     # mostra o que restauraria
python3 -m tooling check     # só a checagem de contraste WCAG
python3 -m tooling render    # só renderiza templates/ em build/
tests/selftest.sh            # prova render, dry-run, idempotência, backup e restore em /tmp
```

### Garantias

- **Idempotente:** rodar `./install.sh` duas vezes seguidas não muda nada na segunda (nem cria backup novo).
- **Backup antes de tocar:** qualquer arquivo existente e o valor antigo de cada chave do KDE vão para `~/.local/state/gibi/backups/<timestamp>/manifest.json`. O `uninstall` restaura, para cada item, o backup mais antigo ainda não restaurado, ou seja, o estado de antes do tema. Se antes não havia nada, volta ao padrão do Plasma (Breeze).
- **Sem sudo para o tema:** tudo vai para `~`. `sudo` só aparece no `pacman -S` de dependências que faltam, e sempre com confirmação.
- **Arquivos que o KDE reescreve** (`kdeglobals`, `kwinrc`, `klassyrc`…) só são alterados chave a chave, com `kwriteconfig6`. Nunca por symlink.
- Alvo cujo app não está instalado é pulado com aviso.

## Dependências

| Pacote | Origem | Usado por |
|---|---|---|
| `python` (>= 3.11, só stdlib) | core | tooling |
| `plasma-workspace`, `kconfig`, `qt6-tools` | extra (já vêm com o Plasma) | `plasma-apply-*`, `kwriteconfig6`, `qdbus6` |
| `inter-font` | extra | fonts |
| `ttf-cascadia-code-nerd` | extra | fonts, ghostty |
| `klassy` | **AUR** (nesta máquina: `klassy-bin`) | klassy, blur |
| `breeze-gtk` | extra | gtk |
| `papirus-icon-theme` | extra | icons |
| `ghostty` | extra (e cachyos-extra-v3) | ghostty |

Pacotes faltando são instalados com confirmação: `sudo pacman -S --needed` para os repositórios oficiais e `paru`/`yay -S --needed` para o AUR.

## Alvos

Rodam nesta ordem. Cada alvo é uma pasta em `targets/` com um `target.toml` e `templates/`.

| Alvo | O que faz |
|---|---|
| `fonts` | Inter na interface, CaskaydiaCove Nerd Font na monoespaçada. Troca só a família e mantém os tamanhos atuais. |
| `kde-colors` | `~/.local/share/color-schemes/Gibi.colors` + `plasma-apply-colorscheme`. |
| `klassy` | Decoração Klassy, `widgetStyle` (fonte única em `palette.toml [kde].widget_style`), barra de título opaca, cantos de 10px, sombras difusas pretas de força moderada. |
| `blur` | Efeito blur do KWin com força baixa, painel em modo translúcido, menus do Klassy a 88% de opacidade. Janelas continuam opacas. |
| `gtk` | `gibi.css` (GTK3 e GTK4/libadwaita) importado no `gtk.css` por bloco gerenciado, e tema GTK3 Breeze. |
| `ghostty` | Tema `gibi` com paleta ANSI + bloco gerenciado no `config.ghostty` (`theme` e `font-family`). |
| `icons` | Tema de ícones `Gibi-Papirus-Dark`: herda o Papirus-Dark e troca só as pastas por marrons. |
| `brave` | Extensão de tema em `~/.local/share/gibi/brave-theme` (carregar manualmente, ver abaixo). |
| `lookandfeel` | Pacote `org.gibi.desktop` sem layout de painéis. Roda por último. |

Alvos com nome começando em `_` (ex.: `_selftest`) só rodam com `--only`.

### Cor das pastas

Padrão: `brown`. Para trocar (por exemplo, para amarelo), edite `palette.toml`:

```toml
[kde]
folder_color = "yellow"   # qualquer cor do Papirus: yellow, grey, orange, palebrown...
```

e rode `./install.sh --only icons`.

**Diferença em relação ao plano original:** o `PHASE-1.md` pedia o `papirus-folders`. Ele altera `/usr/share/icons` com `sudo`, o que viola a regra "sem sudo para arquivos do tema", e cada atualização do `papirus-icon-theme` desfaz a mudança. Em vez disso, o alvo `icons` gera um tema derivado em `~/.local/share/icons/Gibi-Papirus-Dark` com symlinks para as pastas da cor escolhida. O resultado é o mesmo, fica 100% em `~` e o `uninstall` remove. Se preferir o `papirus-folders` mesmo assim: `paru -S papirus-folders` (AUR) e `papirus-folders -C yellow --theme Papirus-Dark` (desfazer: `papirus-folders -D --theme Papirus-Dark`).

### Brave

O Brave não instala tema sem política gerenciada. Depois do install:

1. abra `brave://extensions`;
2. ligue o **Modo do desenvolvedor**;
3. **Carregar sem compactação** → `~/.local/share/gibi/brave-theme`.

Quando o tema mudar, clique em **Recarregar** no card da extensão. O tema do Brave usa só cores planas, sem amarelo.

### GTK

- O `~/.config/gtk-3.0/colors.css` é gerado pelo KDE a partir do esquema de cores e **não** é tocado. O `gtk.css` recebe só um `@import 'gibi.css';` entre marcadores `/* >>> gibi >>> */`, logo depois dos `@import` existentes.
- Temas GTK3 como o Orchis compilam as cores no CSS e ignoram `@define-color`. Por isso o alvo troca o tema GTK3 para **Breeze** (via `kded6 gtkconfig`), que lê as cores do esquema do KDE. O tema anterior vai para o backup e volta no `uninstall`.
- No libadwaita, `accent_bg_color` é o amarelo. Botões "suggested-action" e switches ligados ficam amarelos (tamanho de botão, ok pela regra). A seleção de texto foi forçada para o roxo.

### Ghostty

O Ghostty (>= 1.2) lê `~/.config/ghostty/config` e **depois** `config.ghostty`, e o último vence. Por isso o bloco gerenciado vai no `config.ghostty`, que é criado se não existir. O resto do arquivo não é tocado. Se você tiver `background-opacity` < 1, o terminal continua translúcido; o tema não mexe nisso.

## Regras de cor e onde o amarelo aparece

- `DecorationFocus = accent.primary` no esquema do KDE. No Klassy/Breeze e no Kirigami ele desenha **anéis e bordas de foco**, não preenchimentos. Checkbox marcado, slider e barra de progresso usam `Highlight` (seleção, roxo). Hover usa `DecorationHover = base.70`, então nenhum hover grande fica amarelo.
- Brave: sem amarelo. Ghostty: amarelo só no cursor.
- `python3 -m tooling check` falha o install se um par obrigatório da §5.3 ficar abaixo de 4.5:1. Aviso conhecido: `base.60` (texto desabilitado) sobre `base.100` dá 2.14:1, abaixo dos 3:1 pedidos para tokens "apagados". Não é par obrigatório e o WCAG isenta texto desabilitado, por isso é só aviso.

## Limitações conhecidas

- **Painel:** o alvo liga o modo translúcido, mas o nível exato de opacidade vem do Plasma Style em uso. Não dá para fixar 0.88 sem um Plasma Style próprio.
- **Menus:** translúcidos pela opção `MenuOpacity` do Klassy. Na fase 2 (Kvantum) isso passa para o `.kvconfig`.
- **Look-and-Feel:** o `uninstall` só devolve o *nome* do Look-and-Feel anterior (sem reaplicá-lo), porque cada configuração que o pacote aplica já é restaurada pelo seu próprio alvo.
- **Restore de chaves herdadas:** se um valor vinha em cascata (ex.: `~/.config/kdedefaults`), o restore grava o mesmo valor explicitamente no arquivo do usuário. O efeito é idêntico.

## Estrutura

```
palette.toml        fonte única: cores, forma, tipografia, nome, widget style
install.sh          entrada fina → python3 -m tooling apply
uninstall.sh        entrada fina → python3 -m tooling restore
tooling/            Python stdlib: palette, render, contrast, targets, backup, blocks, kde, icons
targets/<alvo>/     target.toml + templates/ com placeholders ${token}
build/              saída renderizada (ignorada pelo git)
docs/               checklist visual, notas da fase 2, amostra ANSI
tests/selftest.sh   prova da fundação usando targets/_selftest
```

Detalhes de contrato (`palette.toml`, templates, `target.toml`) em `ARCHITECTURE.md`. Além dos campos de lá, o `target.toml` aceita:

- `[[keys]]`: `file`, `group` (string ou lista para grupos aninhados), `key`, `value` | `delete = true` | `transform = "font-family"`;
- `[[states]]`: algo com comando de leitura e escrita. `get`, `set`, `restore` (opcional), `value`, `default` (usado no restore quando não havia valor) e `reapply_on_change`. O valor chega aos comandos em `$GIBI_VALUE`; escreva `$$GIBI_VALUE` no TOML, porque `$` sozinho é placeholder;
- `[[files]]` em `managed-block`: `comment` (`#`, `//`, `/*`, `;`) e `position` (`bottom`, `top`, `after-imports`);
- `order` (ordem de execução) e `message` (texto mostrado quando o alvo muda algo).

## Licença

GPL-3.0-or-later. Ver `LICENSE`.

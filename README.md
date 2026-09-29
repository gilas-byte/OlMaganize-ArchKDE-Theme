# Gibi

> **Créditos:** a paleta e a sensação visual deste tema vêm do **[Primary for Obsidian](https://github.com/primary-theme/obsidian)**, de **Cecilia May**. Ele serviu de inspiração e é a fonte da paleta base. Nenhum código do Primary foi copiado, só os valores de cor.
>
> **Tema Kvantum:** baseado no **KvFlat**, de **Tsu Jan**, um dos temas que acompanham o [Kvantum](https://github.com/tsujan/Kvantum) (licença **GPL-3.0-or-later**). Do KvFlat vieram a estrutura do `.kvconfig` e o conjunto de elementos; o SVG foi redesenhado por `targets/kvantum/generate.py` para ter o efeito de tecla.
>
> **Plasma Style:** baseado no **Breeze** (tema `default` do Plasma, do **KDE Visual Design Group**, licença **LGPL**). Do Breeze vieram os nomes de arquivos, prefixos, elementos `hint-*` e margens; o desenho é refeito por `targets/plasma-style/generate.py`.

Tema retro-moderno para **Arch Linux / CachyOS com KDE Plasma 6**: marrons quentes, texto bege de baixo contraste, sensação de revista antiga e um acento amarelo vivo usado com parcimônia. "Gibi" é um codinome provisório. O nome fica em um único lugar (`palette.toml → [theme]`), então renomear é trocar `id`/`name` lá e rodar `./install.sh` de novo.

## Instalação

```sh
git clone <repo> ~/Documents/gibi-theme && cd ~/Documents/gibi-theme
./install.sh --dry-run       # mostra o que faria, sem alterar nada
./install.sh                 # render + checagem de contraste + aplica todos os alvos detectados
```

Depois do primeiro install, faça **logout/login** uma vez e siga `docs/CHECKLIST-FASE-1.md`, `docs/CHECKLIST-FASE-2.md` e `docs/CHECKLIST-FASE-3.md`.

```sh
./install.sh --only ghostty  # só um alvo (ou vários: --only gtk,ghostty)
./install.sh --list          # lista os alvos, se foram detectados e dependências faltando
./uninstall.sh               # restaura arquivos e chaves do KDE ao estado anterior
./uninstall.sh --dry-run     # mostra o que restauraria
python3 -m tooling check     # só a checagem de contraste WCAG
python3 -m tooling render    # só renderiza templates/ em build/
tests/selftest.sh            # prova render, dry-run, idempotência, backup e restore em /tmp
tests/kvantum-check.py       # alvo kvantum: sem hex solto, templates em dia, elementos completos
tests/kvantum-preview.py     # fotografa os widgets com o tema Kvantum (offscreen) em build/
tests/plasma-style-check.py  # alvo plasma-style: sem hex solto, templates em dia, nada faltando vs. Breeze
tests/plasma-style-preview.py # barras, tarefas, popup e controles do Plasma com o KSvg real (offscreen)
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
| `klassy` | **AUR** (nesta máquina: `klassy-bin`) | klassy |
| `kvantum` (Qt6) | extra (nesta máquina: `kvantum-qt6-git`, que provê `kvantum`) | kvantum |
| `kvantum-qt5` | extra; só se `qt5-base` estiver instalado | kvantum-qt5 |
| `python-pyqt6` | extra; opcional | `tests/kvantum-preview.py`, `tests/plasma-style-preview.py` |
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
| `klassy` | Decoração de janela Klassy: barra de título opaca, cantos de 10px, sombras difusas pretas de força moderada. |
| `kvantum` | Tema Kvantum `Gibi` (widgets com efeito de tecla) em `~/.config/Kvantum/Gibi/`, `theme=Gibi` no `kvantum.kvconfig` e `widgetStyle` (fonte única em `palette.toml [kde].widget_style`). Menus e popups a 88% com blur. |
| `kvantum-qt5` | Só garante o pacote `kvantum-qt5` quando há Qt5 no sistema (ex.: VLC 3). O tema é o mesmo. |
| `blur` | Efeito blur do KWin com força baixa e painel em modo translúcido. Janelas continuam opacas. |
| `plasma-style` | Plasma Style `Gibi` em `~/.local/share/plasma/desktoptheme/Gibi` + `plasma-apply-desktoptheme`: barras, tarefas com cara de tecla, popups, notificações, dicas e controles do Plasma. |
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

### Kvantum (fase 2)

- **Nada de hex nos templates.** `targets/kvantum/generate.py` lê a geometria da paleta (raios, `keycap.*`, anel de foco) e escreve `templates/theme.svg` e `templates/theme.kvconfig` com as cores ainda como `${token}`. Ele roda sozinho antes do render (chave `generate` do `target.toml`), então mudar um raio no `palette.toml` e rodar `./install.sh` redesenha o tema. Não edite os dois templates à mão: edite o gerador ou `theme.kvconfig.in`.
- Cada widget do Kvantum é desenhado com 9 fatias por estado (cantos, bordas, interior). O gerador descreve cada elemento como camadas de retângulos arredondados e fatia por recorte de polígono, porque o QtSvg não entende `clipPath`, filtros nem `rgba()`. Tokens `rgba(...)` da paleta viram `${x_hex}` + `${x_alpha}` (e sombras `x y blur rgba()` ganham também `${x_x}`, `${x_y}`, `${x_blur}`).
- **Tecla:** face `base.90`, brilho de 1px no topo, borda interna, base inferior de 3px e sombra curta de 2px. Hover `base.80`; pressionado `base.110` sem base nem sombra, com a face 1px mais baixa; marcado em `selection.bg`; foco = anel de 2px amarelo a 45%.
- **Menus:** translucidez (`surface.float_opacity`) e sombra vêm do SVG; `popup_blurring=true` pede ao KWin o blur atrás. A opção `MenuOpacity` do Klassy saiu do alvo `blur` (não tem mais efeito com o Kvantum desenhando os widgets).
- **Preview sem mexer no sistema:** `python3 tests/kvantum-preview.py` renderiza os widgets offscreen em `build/kvantum-preview*.png`.

### Plasma Style (fase 3)

- Mesmo esquema do Kvantum: `targets/plasma-style/generate.py` escreve `templates/theme/` (SVGs, `metadata.json`, `plasmarc`) com as cores como `${token}`; o fatiamento e as camadas de tecla/campo moram em `tooling/svgslice.py`, compartilhado com o gerador do Kvantum. Os SVGs são `.svg` sem compressão (o KSvg do Plasma 6 carrega normalmente).
- **Barras:** `base.100` a 0.88 com blur (0.88 exato agora, porque vem do nosso SVG), borda de 1px `base.70` no lado voltado para a tela; flutuante, borda nos 4 lados, cantos de 10px e sombra suave.
- **Tarefas:** sem fundo em repouso; hover = tecla; janela ativa = tecla com face roxa-escura (`selection.bg_subtle`); janela pedindo atenção = tecla com borda e base amarelas (o único amarelo da barra); minimizada = plana e apagada; tarefas agrupadas ganham um selo roxo com "+".
- **Popups, notificações, dicas:** iguais aos menus do Kvantum (`base.90` a 0.88, borda `base.70`, cantos de 10px, sombra em camadas); cabeçalho dos popups em `base.110` com linha fina.
- **Controles do Plasma:** botão de tecla, campo afundado com anel amarelo no foco, checkbox/radio/switch ligados em roxo, slider e progresso com preenchimento roxo, aba ativa com linha amarela de 2px.
- **Cache:** a versão em `metadata.json` leva um hash da paleta e dos templates, então o Plasma descarta o cache de SVGs sempre que o tema muda.
- **Preview sem mexer no sistema:** `python3 tests/plasma-style-preview.py` usa o KSvg de verdade num ambiente temporário e grava `build/plasma-style-preview.png`.
- O que o tema não desenha cai no Breeze, que segue o esquema `Gibi.colors` (ex.: calendário, relógio analógico, medidores, `busywidget`, `listitem`, `frame`, `toolbar`).

### Ghostty

O Ghostty (>= 1.2) lê `~/.config/ghostty/config` e **depois** `config.ghostty`, e o último vence. Por isso o bloco gerenciado vai no `config.ghostty`, que é criado se não existir. O resto do arquivo não é tocado. Se você tiver `background-opacity` < 1, o terminal continua translúcido; o tema não mexe nisso.

## Regras de cor e onde o amarelo aparece

- `DecorationFocus = accent.primary` no esquema do KDE. No Klassy/Breeze e no Kirigami ele desenha **anéis e bordas de foco**, não preenchimentos. Checkbox marcado, slider e barra de progresso usam `Highlight` (seleção, roxo). Hover usa `DecorationHover = base.70`, então nenhum hover grande fica amarelo.
- Brave: sem amarelo. Ghostty: amarelo só no cursor.
- `python3 -m tooling check` falha o install se um par obrigatório da §5.3 ficar abaixo de 4.5:1. Aviso conhecido: `base.60` (texto desabilitado) sobre `base.100` dá 2.14:1, abaixo dos 3:1 pedidos para tokens "apagados". Não é par obrigatório e o WCAG isenta texto desabilitado, por isso é só aviso.

## Limitações conhecidas

- **Botões do Plasma com raio menor:** botões e campos dos popups do Plasma usam `radius_s` (4px) em vez de `radius_m`. O Plasma desenha a caixa do checkbox com o mesmo frame do botão, num quadrado de 16px, e com 7px de raio ela viraria um círculo igual ao radio. Botões dos apps (Kvantum) e tarefas da barra continuam com 7px.
- **Tarefa ativa em roxo:** o plano pedia face `base.90` para a janela ativa, mas ela ficava indistinguível do hover (`base.80`). A janela ativa usa `selection.bg_subtle`.
- **Plasmoides no desktop sem blur do papel de parede:** o Breeze tem um prefixo opcional `blurred` para isso; o Gibi não desenha, então widgets soltos no desktop usam o fundo translúcido comum.
- **Sombras de barras e popups** são desenhadas pelo KWin a partir das peças `shadow-*`; o preview offscreen mostra as peças, mas não a composição real.
- **Botão padrão (Kvantum):** o plano pedia face amarela com texto escuro. O Kvantum usa a mesma cor de texto para todos os botões (não existe cor de texto só para o botão padrão) e desenha o elemento `-default` por cima de qualquer estado, então o texto bege ficaria ilegível sobre o amarelo. O botão padrão é uma tecla normal com **borda e base inferior amarelas** e texto em negrito. Continua sendo o único botão com amarelo.
- **Conteúdo do botão pressionado não desce 1px:** o deslocamento de conteúdo (`PM_ButtonShiftVertical`) está fixo em 0 no código do Kvantum (a opção existe comentada). A sensação de tecla apertada vem da face, que desce 1px e perde a base e a sombra.
- **Apps QML/Kirigami** (boa parte das Configurações do Sistema, Discover, partes do Plasma) usam o `qqc2-desktop-style`, que só aproveita parte do estilo Qt. Neles o efeito de tecla aparece incompleto ou não aparece; as cores vêm do esquema `Gibi.colors` de qualquer jeito.
- **Kvantum ausente:** se o pacote `kvantum` não for instalado, o alvo `kvantum` é pulado, mas o Look-and-Feel ainda aponta `widgetStyle=kvantum` e o Qt cai no estilo padrão (sem o efeito de tecla). Para voltar ao Klassy nesse caso, use `widget_style = "Klassy"` no `palette.toml`.
- **Look-and-Feel:** o `uninstall` só devolve o *nome* do Look-and-Feel anterior (sem reaplicá-lo), porque cada configuração que o pacote aplica já é restaurada pelo seu próprio alvo.
- **Restore de chaves herdadas:** se um valor vinha em cascata (ex.: `~/.config/kdedefaults`), o restore grava o mesmo valor explicitamente no arquivo do usuário. O efeito é idêntico.

## Estrutura

```
palette.toml        fonte única: cores, forma, tipografia, nome, widget style
install.sh          entrada fina → python3 -m tooling apply
uninstall.sh        entrada fina → python3 -m tooling restore
tooling/            Python stdlib: palette, render, contrast, targets, backup, blocks, kde, icons, svgslice
targets/<alvo>/     target.toml + templates/ com placeholders ${token}
build/              saída renderizada (ignorada pelo git)
docs/               checklists visuais das fases 1, 2 e 3, notas da fase 2, amostra ANSI
tests/              selftest.sh (fundação), kvantum-{check,preview}.py, plasma-style-{check,preview}.py
```

Detalhes de contrato (`palette.toml`, templates, `target.toml`) em `ARCHITECTURE.md`. Além dos campos de lá, o `target.toml` aceita:

- `[[keys]]`: `file`, `group` (string ou lista para grupos aninhados), `key`, `value` | `delete = true` | `transform = "font-family"`;
- `[[states]]`: algo com comando de leitura e escrita. `get`, `set`, `restore` (opcional), `value`, `default` (usado no restore quando não havia valor) e `reapply_on_change`. O valor chega aos comandos em `$GIBI_VALUE`; escreva `$$GIBI_VALUE` no TOML, porque `$` sozinho é placeholder;
- `[[files]]` em `managed-block`: `comment` (`#`, `//`, `/*`, `;`) e `position` (`bottom`, `top`, `after-imports`);
- `order` (ordem de execução) e `message` (texto mostrado quando o alvo muda algo);
- `generate`: script Python (relativo ao alvo) que roda antes do render e (re)escreve `templates/` a partir da paleta. Deve ser determinístico e só gravar o que mudou.

## Licença

GPL-3.0-or-later. Ver `LICENSE`.

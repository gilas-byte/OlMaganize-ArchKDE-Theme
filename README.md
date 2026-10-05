# Gibi

> **Créditos:** a paleta e a sensação visual deste tema vêm do **[Primary for Obsidian](https://github.com/primary-theme/obsidian)**, de **Cecilia May**. Ele serviu de inspiração e é a fonte da paleta base. Nenhum código do Primary foi copiado, só os valores de cor.
>
> **Tema Kvantum:** baseado no **KvFlat**, de **Tsu Jan**, um dos temas que acompanham o [Kvantum](https://github.com/tsujan/Kvantum) (licença **GPL-3.0-or-later**). Do KvFlat vieram a estrutura do `.kvconfig` e o conjunto de elementos; o SVG foi redesenhado por `targets/kvantum/generate.py` para ter o efeito de tecla.
>
> **Plasma Style:** baseado no **Breeze** (tema `default` do Plasma, do **KDE Visual Design Group**, licença **LGPL**). Do Breeze vieram os nomes de arquivos, prefixos, elementos `hint-*` e margens; o desenho é refeito por `targets/plasma-style/generate.py`.
>
> **Páginas web (Stylus):** os estilos vêm do **[Catppuccin Userstyles](https://github.com/catppuccin/userstyles)** (**Catppuccin Org**, licença **MIT**, texto em `targets/stylus/LICENSE-catppuccin-userstyles`), fixados como submodule em `vendor/catppuccin-userstyles`. `targets/stylus/generate.py` troca só a paleta (e o header) de cada estilo; o CSS de cada site é do Catppuccin.
>
> **YASB (Windows):** `targets/yasb/templates/gibi.css` redefine as variáveis dos dois estilos que acompanham o **[YASB](https://github.com/amnweb/yasb)** (**amnweb**, licença **MIT**): o "i3-style" (`--bar_bg`, `--text`...) e o do assistente (`--yasb-*`). Só os nomes vêm do YASB; os valores e as regras são do Gibi.
>
> **Windhawk (Windows):** os alvos `windhawk-*` geram configurações para os mods *Windows 11 Start Menu Styler*, *Notification Center Styler* e *File Explorer Styler*, de **m417z** (autor do **[Windhawk](https://windhawk.net)**). Os nomes dos elementos XAML vêm dos temas embutidos nesses mods (`TintedGlass`, `TranslucentStartMenu`); nenhum código foi copiado, e as cores são da paleta.

Tema retro-moderno para **Arch Linux / CachyOS com KDE Plasma 6**, e desde a W1 também para o **Windows 11** (ver [Windows](#windows)): marrons quentes, texto bege de baixo contraste, sensação de revista antiga e um acento amarelo vivo usado com parcimônia. "Gibi" é um codinome provisório. O nome fica em um único lugar (`palette.toml → [theme]`), então renomear é trocar `id`/`name` lá e rodar `./install.sh` de novo.

## Instalação

```sh
git clone --recursive <repo> ~/Documents/gibi-theme && cd ~/Documents/gibi-theme
# já clonou sem --recursive? git submodule update --init
./install.sh --dry-run       # mostra o que faria, sem alterar nada
./install.sh                 # render + checagem de contraste + aplica todos os alvos detectados
```

Depois do primeiro install, faça **logout/login** uma vez e siga `docs/CHECKLIST-FASE-1.md`, `docs/CHECKLIST-FASE-2.md`, `docs/CHECKLIST-FASE-3.md` e `docs/CHECKLIST-FASE-4.md`.

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
tests/stylus-check.py        # alvo stylus: lib, filtros, import.json, contraste (+ compila tudo se houver node/less)
```

### Garantias

- **Idempotente:** rodar `./install.sh` duas vezes seguidas não muda nada na segunda (nem cria backup novo).
- **Mudou só a paleta?** Alvos que usam symlink para `build/` não veem o link mudar, então o instalador guarda um hash do conteúdo aplicado em `~/.local/state/gibi/rendered/`. Se o render mudou, o alvo conta como alterado: roda os `post` (ex.: o Kvantum avisa os apps) e o `reapply_on_change` (ex.: o Plasma Style passa um instante pelo Breeze para recarregar, porque o `plasma-apply-desktoptheme` não reaplica o tema ativo).
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
| `vendor/catppuccin-userstyles` | submodule git (`--recursive`) | stylus |
| `nodejs` + `less` (npm) | extra / npm; opcional | compilação em `tests/stylus-check.py` |

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
| `stylus` | `~/.local/share/gibi/stylus/import.json` com os userstyles do Catppuccin recoloridos para a paleta (importar no Stylus, ver abaixo). |
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

### Stylus (fase 4)

O conteúdo das páginas vem dos userstyles do Catppuccin, via extensão **Stylus**. Os estilos não têm cor própria: todos leem 26 cores por nome (`@base`, `@text`, `@red`...) de uma lib compartilhada. O alvo troca os valores dessa lib pelos da paleta, então os 134 estilos são recoloridos de uma vez.

Depois do install:

1. no Stylus, **apague ou desative** os estilos "… Catppuccin" (senão os dois ficam ativos em cada site e brigam);
2. ícone do Stylus → **Gerenciar** → **Importar** → `~/.local/share/gibi/stylus/import.json`.

O que o gerador faz com cada estilo:

- **Paleta:** um flavor só, `gibi`. Mapa dos slots em `targets/stylus/generate.py` (`SLOTS`), com os slots sem token próprio em `palette.toml [web]`. `mauve` e `lavender` mantêm o nome (os estilos citam), mas valem amarelo suave e tan: nada de roxo. Os nomes antigos de flavor (`latte`, `mocha`...) são apelidos do `gibi`, para os estilos que citam flavor direto.
- **Accent:** padrão amarelo suave (`accent.secondary`), escolhível por estilo nas opções do Stylus. "Amarelo vivo" (`accent.primary`) existe como opção, mas **fura a regra 3.4.1** em sites que usam o accent em áreas grandes: use por sua conta.
- **Filtros de ícone:** as cadeias `filter:` que recolorem SVGs pretos são recalculadas para cada cor (ver `docs/STYLUS-FILTERS.md`).
- **Header:** `@name "<site> Gibi"`, `@namespace` próprio (não colide com os do Catppuccin), **sem `@updateURL`**. Se ficasse, o Stylus trocaria o estilo pelo original na checagem de 24h.
- **Lib embutida** em cada estilo: nada é carregado de `userstyles.catppuccin.com`.
- **Só alguns sites?** `palette.toml [stylus] include = ["github", "youtube"]` (nomes das pastas em `vendor/catppuccin-userstyles/styles/`). Vazio = todos.
- **Atualizar o upstream:** `git -C vendor/catppuccin-userstyles pull`, atualize o SHA em `targets/stylus/UPSTREAM`, rode `tests/stylus-check.py` e commite o submodule.

`build/stylus-report.md` lista as cores que os estilos escrevem à mão (ver Limitações).

### GTK

- O `~/.config/gtk-3.0/colors.css` é gerado pelo KDE a partir do esquema de cores e **não** é tocado. O `gtk.css` recebe só um `@import 'gibi.css';` entre marcadores `/* >>> gibi >>> */`, logo depois dos `@import` existentes.
- Temas GTK3 como o Orchis compilam as cores no CSS e ignoram `@define-color`. Por isso o alvo troca o tema GTK3 para **Breeze** (via `kded6 gtkconfig`), que lê as cores do esquema do KDE. O tema anterior vai para o backup e volta no `uninstall`.
- No libadwaita, `accent_bg_color` é o amarelo. Botões "suggested-action" e switches ligados ficam amarelos (tamanho de botão, ok pela regra). A seleção de texto foi forçada para o marrom-dourado da seleção.

### Kvantum (fase 2)

- **Nada de hex nos templates.** `targets/kvantum/generate.py` lê a geometria da paleta (raios, `keycap.*`, anel de foco) e escreve `templates/theme.svg` e `templates/theme.kvconfig` com as cores ainda como `${token}`. Ele roda sozinho antes do render (chave `generate` do `target.toml`), então mudar um raio no `palette.toml` e rodar `./install.sh` redesenha o tema. Não edite os dois templates à mão: edite o gerador ou `theme.kvconfig.in`.
- Cada widget do Kvantum é desenhado com 9 fatias por estado (cantos, bordas, interior). O gerador descreve cada elemento como camadas de retângulos arredondados e fatia por recorte de polígono, porque o QtSvg não entende `clipPath`, filtros nem `rgba()`. Tokens `rgba(...)` da paleta viram `${x_hex}` + `${x_alpha}` (e sombras `x y blur rgba()` ganham também `${x_x}`, `${x_y}`, `${x_blur}`).
- **Tecla:** face `base.90`, brilho de 1px no topo, borda interna, base inferior de 3px e sombra curta de 2px. Hover `base.80`; pressionado `base.110` sem base nem sombra, com a face 1px mais baixa; marcado em `selection.bg`; foco = anel de 2px amarelo a 45%.
- **Menus:** translucidez (`surface.float_opacity`) e sombra vêm do SVG; `popup_blurring=true` pede ao KWin o blur atrás. A opção `MenuOpacity` do Klassy saiu do alvo `blur` (não tem mais efeito com o Kvantum desenhando os widgets).
- **Preview sem mexer no sistema:** `python3 tests/kvantum-preview.py` renderiza os widgets offscreen em `build/kvantum-preview*.png`.

### Plasma Style (fase 3)

- Mesmo esquema do Kvantum: `targets/plasma-style/generate.py` escreve `templates/theme/` (SVGs, `metadata.json`, `plasmarc`) com as cores como `${token}`; o fatiamento e as camadas de tecla/campo moram em `tooling/svgslice.py`, compartilhado com o gerador do Kvantum. Os SVGs são `.svg` sem compressão (o KSvg do Plasma 6 carrega normalmente).
- **Barras:** `base.100` a 0.88 com blur (0.88 exato agora, porque vem do nosso SVG), borda de 1px `base.70` no lado voltado para a tela; flutuante, borda nos 4 lados, cantos de 10px e sombra suave.
- **Tarefas:** app aberto sem foco = só uma barrinha bege na borda voltada para a tela (apagada se minimizado); hover = tecla; janela ativa = tecla com face marrom-dourada (`selection.bg_subtle`) e barrinha amarela; janela pedindo atenção = tecla com borda e base amarelas (o único amarelo da barra); tarefas agrupadas ganham um selo amarelo com "+".
- **Popups, notificações, dicas:** iguais aos menus do Kvantum (`base.90` a 0.88, borda `base.70`, cantos de 10px, sombra em camadas); cabeçalho dos popups em `base.110` com linha fina.
- **Controles do Plasma:** botão de tecla, campo afundado com anel amarelo no foco, checkbox/radio/switch ligados em amarelo suave (`accent.secondary`), slider e progresso preenchidos com ele, aba ativa com linha amarela de 2px.
- **Cache:** a versão em `metadata.json` leva um hash da paleta e dos templates, então o Plasma descarta o cache de SVGs sempre que o tema muda.
- **Preview sem mexer no sistema:** `python3 tests/plasma-style-preview.py` usa o KSvg de verdade num ambiente temporário e grava `build/plasma-style-preview.png`.
- O que o tema não desenha cai no Breeze, que segue o esquema `Gibi.colors` (ex.: calendário, relógio analógico, medidores, `busywidget`, `listitem`, `frame`, `toolbar`).

### Ghostty

O Ghostty (>= 1.2) lê `~/.config/ghostty/config` e **depois** `config.ghostty`, e o último vence. Por isso o bloco gerenciado vai no `config.ghostty`, que é criado se não existir. O resto do arquivo não é tocado. Se você tiver `background-opacity` < 1, o terminal continua translúcido; o tema não mexe nisso.

## Regras de cor e onde o amarelo aparece

- `DecorationFocus = accent.primary` no esquema do KDE. No Klassy/Breeze e no Kirigami ele desenha **anéis e bordas de foco**, não preenchimentos. Checkbox marcado, slider e barra de progresso usam `Highlight` (seleção, marrom-dourada) no Breeze/Klassy e o amarelo suave (`accent.secondary`) no Kvantum e no Plasma Style. Hover usa `DecorationHover = base.70`, então nenhum hover grande fica amarelo.
- Brave: sem amarelo. Ghostty: amarelo só no cursor.
- `python3 -m tooling check` falha o install se um par obrigatório da §5.3 ficar abaixo de 4.5:1. Aviso conhecido: `base.60` (texto desabilitado) sobre `base.100` dá 2.14:1, abaixo dos 3:1 pedidos para tokens "apagados". Não é par obrigatório e o WCAG isenta texto desabilitado, por isso é só aviso.

## Limitações conhecidas

- **Botões do Plasma com raio menor:** botões e campos dos popups do Plasma usam `radius_s` (4px) em vez de `radius_m`. O Plasma desenha a caixa do checkbox com o mesmo frame do botão, num quadrado de 16px, e com 7px de raio ela viraria um círculo igual ao radio. Botões dos apps (Kvantum) e tarefas da barra continuam com 7px.
- **Tarefa ativa na cor da seleção:** o plano pedia face `base.90` para a janela ativa, mas ela ficava indistinguível do hover (`base.80`). A janela ativa usa `selection.bg_subtle`.
- **Plasmoides no desktop sem blur do papel de parede:** o Breeze tem um prefixo opcional `blurred` para isso; o Gibi não desenha, então widgets soltos no desktop usam o fundo translúcido comum.
- **Sombras de barras e popups** são desenhadas pelo KWin a partir das peças `shadow-*`; o preview offscreen mostra as peças, mas não a composição real.
- **Botão padrão (Kvantum):** o plano pedia face amarela com texto escuro. O Kvantum usa a mesma cor de texto para todos os botões (não existe cor de texto só para o botão padrão) e desenha o elemento `-default` por cima de qualquer estado, então o texto bege ficaria ilegível sobre o amarelo. O botão padrão é uma tecla normal com **borda e base inferior amarelas** e texto em negrito. Continua sendo o único botão com amarelo.
- **Conteúdo do botão pressionado não desce 1px:** o deslocamento de conteúdo (`PM_ButtonShiftVertical`) está fixo em 0 no código do Kvantum (a opção existe comentada). A sensação de tecla apertada vem da face, que desce 1px e perde a base e a sombra.
- **Apps QML/Kirigami** (boa parte das Configurações do Sistema, Discover, partes do Plasma) usam o `qqc2-desktop-style`, que só aproveita parte do estilo Qt. Neles o efeito de tecla aparece incompleto ou não aparece; as cores vêm do esquema `Gibi.colors` de qualquer jeito.
- **Kvantum ausente:** se o pacote `kvantum` não for instalado, o alvo `kvantum` é pulado, mas o Look-and-Feel ainda aponta `widgetStyle=kvantum` e o Qt cai no estilo padrão (sem o efeito de tecla). Para voltar ao Klassy nesse caso, use `widget_style = "Klassy"` no `palette.toml`.
- **Look-and-Feel:** o `uninstall` só devolve o *nome* do Look-and-Feel anterior (sem reaplicá-lo), porque cada configuração que o pacote aplica já é restaurada pelo seu próprio alvo.
- **Restore de chaves herdadas:** se um valor vinha em cascata (ex.: `~/.config/kdedefaults`), o restore grava o mesmo valor explicitamente no arquivo do usuário. O efeito é idêntico.

- **Stylus: cores escritas à mão.** 58 estilos têm hex literal no código (488 ocorrências; GitHub, tldraw, proton, twitter, duckduckgo...). Elas não passam pela lib e aparecem com a cor original, em geral pastel, no meio do marrom. Por volta de 278 estão em seletores (`[fill="#fff"]`) e não pintam nada; o resto pinta. Lista completa em `build/stylus-report.md`. Não há remapeamento automático (quebraria SVG e gradiente sem avisar); retoques por site ficam para a fase 4.1.
- **Stylus: syntax highlight pela rede.** Alguns estilos importam CSS de realce de código (`unpkg.com/@catppuccin/highlightjs`, `python.catppuccin.com`, `prismjs.catppuccin.com`). Esse CSS lê as variáveis `--ctp-*`, então segue a paleta, mas é baixado na hora de usar.
- **Stylus: contraste.** Sobre o fundo `base.100`: `red` 4.08:1 e `maroon` 4.28:1 (o mesmo `sem.red` do terminal) e `overlay0` 2.14:1 (= `base.60`), que 16 estilos usam como cor de texto (lista no relatório). Se incomodar, dá para clarear só esses slots em `[web]`.
- **Stylus: reimportar.** Ainda não confirmado se o Stylus atualiza ou duplica um estilo com o mesmo `@namespace`. Até confirmar: apague os "… Gibi" antes de importar uma versão nova.
- **Stylus: bug do upstream corrigido.** `pronouns.cc` e `google-drive` chamam `#lib.rgbify(...)` sem o `[]` em 6 propriedades. O less 4.2.2 (o do upstream) gerava `[object Object]` ali; o less do Stylus recusa o estilo inteiro ("Rulesets cannot be evaluated on a property"), inclusive nos originais do Catppuccin. O gerador acrescenta o `[]` (`fix_upstream` em `generate.py`), e os 134 compilam no less 4.2.2 e no 4.9.

## Windows

Mesmo repo, mesmo `palette.toml`, mesmas regras de cor. Plano completo em `PHASE-WindowsOnly.md`; o que foi testado e decidido antes de escrever os alvos está em `docs/SPIKE-S0.md` (W1) e `docs/SPIKE-S1.md` (W2). A W1 e a W2 são as camadas seguras: **nada pede admin**. O `.msstyles` (W3) ainda não existe.

Requisitos: Windows 11 e Python >= 3.11 (instalação por usuário serve, mesmo fora do PATH: o `install.ps1` procura em `py -3`, `python` e `%LOCALAPPDATA%\Programs\Python\`; ou defina `GIBI_PYTHON`). Sem Python: `winget install --id Python.Python.3.13 --scope user`.

```powershell
git clone --recursive <repo> gibi-theme; cd gibi-theme
# O Windows não roda .ps1 baixado sem liberar; -ExecutionPolicy Bypass vale só para este comando.
powershell -ExecutionPolicy Bypass -File .\install.ps1 -DryRun     # mostra o que faria
powershell -ExecutionPolicy Bypass -File .\install.ps1             # aplica os alvos detectados
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Only yasb,windows-terminal
powershell -ExecutionPolicy Bypass -File .\install.ps1 -List
powershell -ExecutionPolicy Bypass -File .\uninstall.ps1 -DryRun   # mostra o que restauraria
powershell -ExecutionPolicy Bypass -File .\uninstall.ps1           # restaura arquivos e registro
powershell -ExecutionPolicy Bypass -File .\tests\selftest.ps1      # prova tudo em pasta e chave temporárias
```

Depois do primeiro install, siga `docs/CHECKLIST-W1.md` e `docs/CHECKLIST-W2.md`. Screenshots: `tests\screenshot.ps1 -Name <app> [-Window]`.

| Alvo | O que faz |
|---|---|
| `win-fonts` | Inter (v4.1) e CaskaydiaCove Nerd Font (v3.5.1) **instaladas só para o seu usuário**, baixadas dos releases oficiais com SHA-256 fixado (cache em `%LOCALAPPDATA%\gibi\cache`). Fonte já instalada para todos os usuários é pulada. |
| `win-colors` | Modo escuro e cor de destaque `accent.primary` (`#FFEA00`) no registro (HKCU). "Cor de destaque no Iniciar/barra de tarefas" e "nas barras de título" ficam **desligadas**, senão o amarelo pintaria áreas grandes (regra 3.4.1). |
| `windows-terminal` | Fragmento em `%LOCALAPPDATA%\Microsoft\Windows Terminal\Fragments\gibi\` com o esquema `Gibi` (ANSI igual ao Ghostty) e a fonte mono nos perfis Windows PowerShell e Prompt de Comando. O `settings.json` não é tocado. Vale para Store, Preview e instalação sem pacote. |
| `yasb` | `gibi.css` em `%USERPROFILE%\.config\yasb\` (ou `YASB_CONFIG_HOME`) e um `@import "gibi.css";` num bloco gerenciado **no fim** do `styles.css`. O `config.yaml` não é tocado. Recolore a barra pelas variáveis do estilo do YASB e acrescenta o efeito de tecla nos widgets. |
| `brave` | A mesma extensão de tema do Linux, em `%LOCALAPPDATA%\gibi\brave-theme` (carregar sem compactação, como no Linux). |
| `stylus` | O mesmo `import.json`, em `%LOCALAPPDATA%\gibi\stylus\import.json`. |
| `windhawk-start` | **W2.** Configuração do mod *Windows 11 Start Menu Styler*: painel do Iniciar em `base.90` a 0.88 com blur, borda `base.70`, cantos de 10px, busca como campo afundado. Só cor, sem mudar o layout. |
| `windhawk-notifications` | **W2.** *Windows 11 Notification Center Styler*: central, calendário, configurações rápidas, mídia, notificações e jump lists como os popups do Plasma Style. |
| `windhawk-explorer` | **W2.** *Windows 11 File Explorer Styler*: abas, barra de comandos, endereço/busca e as telas Início/Galeria em marrom opaco. Substitui a configuração que o mod tinha (a anterior vai para o backup). |

**Windhawk (W2): passo manual.** A configuração dos mods mora em HKLM e só admin grava lá (`docs/SPIKE-S1.md`), então o tema não aplica nada no Windhawk. O install gera `%LOCALAPPDATA%\gibi\windhawk\<mod>.yaml` e imprime o passo a passo: copiar com `Get-Content ... | Set-Clipboard`, abrir o mod > Configurações > **Textual mode**, colar por cima e **Salvar configurações** (os dois stylers que faltarem: instale antes em Windhawk > Explorar). A cada install, o tooling lê (só lê) a configuração atual e diz se o mod já está com a do Gibi ou se falta colar. Antes, ele exporta a configuração que o mod tinha para o backup, e o `uninstall` mostra esse arquivo para colar de volta. O Taskbar Styler não é tocado (a barra é o YASB).

O que muda em relação ao Linux:

- **Estado e backups** em `%LOCALAPPDATA%\gibi\state\` (no Linux, `~/.local/state/gibi/`). Mesmo `manifest.json`, agora com o valor antigo de cada chave do registro; o `uninstall` devolve o valor ou apaga a chave/valor que não existia.
- **`copy` no lugar de `symlink`:** symlink no Windows pede admin ou modo desenvolvedor. A mudança de conteúdo é detectada comparando a cópia com `build/`.
- **Registro só em HKCU** (o backend recusa qualquer outra raiz), o equivalente do `kwriteconfig6`.
- **Bloco gerenciado preserva a quebra de linha** do arquivo do usuário (o `styles.css` em LF continua LF).
- Alvos Linux não são renderizados nem listados no Windows, e vice-versa (`platforms` no `target.toml`).

Limitações conhecidas (W1 e W2):

- **Cor de destaque:** nesta máquina, registro + `WM_SETTINGCHANGE` bastou, sem logoff (`docs/SPIKE-S0.md`, resultado ao vivo). Se algum componente ficar com a cor antiga, um logoff resolve. Os tons claros/escuros do destaque são uma mistura simples com branco/preto, não o algoritmo do Windows (que não é público).
- **Windhawk sem automação:** cada mudança na paleta pede colar os três YAML de novo (o install avisa com `pendente`). O uninstall também não mexe no Windhawk: ele só aponta o arquivo para colar de volta.
- **Explorer pela metade:** o File Explorer Styler pinta a parte XAML (abas, barras, Início, Galeria). A lista de arquivos e a árvore lateral são Win32 e continuam no escuro padrão do Windows até a W3.
- **Alvos XAML podem mudar com atualizações do Windows:** os nomes dos elementos (`Border#AcrylicBorder`, `Grid#NotificationCenterGrid`...) vêm dos temas dos próprios stylers e funcionam no build 26300; uma atualização pode renomear algum e a peça volta ao padrão, sem quebrar nada.
- **Fonte da interface do Windows continua Segoe UI.** Trocar exige HKLM (admin); a W1 só instala as fontes para os apps que o tema configura.
- **Nome GDI da Nerd Font:** o Windows lista a mono como `CaskaydiaCove NF`; o Windows Terminal aceita o nome do `palette.toml` (`CaskaydiaCove Nerd Font`).
- **Windows Terminal:** só os dois perfis padrão recebem o esquema; nos outros, escolha "Gibi" pela interface. Esquema ou fonte definidos por você no `settings.json` vencem o fragmento.
- **YASB:** o efeito de tecla depende de como o Qt desenha bordas de cores diferentes com raio; está no checklist para validar. O `gibi.css` conhece as variáveis dos dois estilos do YASB; um `styles.css` com nomes próprios só recebe as regras genéricas (barra, `.widget-container`, menus). A fonte da barra não muda (os ícones dependem da fonte que você escolheu).
- **Uninstall de fonte em uso:** se o terminal ou o YASB estiverem com a fonte aberta, o arquivo não sai; o uninstall avisa e basta apagá-lo depois de fechar o app (ou após logoff).
- **Apps WinUI** (Configurações etc.) só recebem o modo escuro e a cor de destaque, sem efeito de tecla (`PHASE-WindowsOnly.md` §8).
- **Testes Linux:** a W1 e a W2 foram escritas numa máquina Windows sem WSL. `tests/linux-invariants.py` prova que os caminhos novos ficam inertes no Linux, mas `tests/selftest.sh` e os checks das fases 2 a 4 precisam rodar numa máquina Arch.

## Estrutura

```
palette.toml        fonte única: cores, forma, tipografia, nome, widget style
install.sh          entrada fina → python3 -m tooling apply
uninstall.sh        entrada fina → python3 -m tooling restore
install.ps1         Windows: entrada fina → python -m tooling apply (acha o Python, liga PYTHONUTF8)
uninstall.ps1       Windows: entrada fina → python -m tooling restore
tooling/            Python stdlib: palette, render, contrast, targets, backup, blocks, kde, icons, svgslice, platform
tooling/backends/   Windows: registry (winreg), fonts (instalação por usuário), winapi (ctypes)
targets/<alvo>/     target.toml + templates/ com placeholders ${token}
vendor/             submodules (catppuccin-userstyles, lido pelo alvo stylus)
build/              saída renderizada (ignorada pelo git)
docs/               checklists visuais das fases 1 a 4, da W1 e da W2, spikes S0 e S1, notas da fase 2, filtros do stylus, amostra ANSI
tests/              selftest.sh (fundação + stylus), kvantum-{check,preview}.py, plasma-style-{check,preview}.py, stylus-check.py,
                    selftest.ps1 + linux-invariants.py + windhawk-check.py + screenshot.ps1 + win-accent-probe.ps1 (Windows)
```

Detalhes de contrato (`palette.toml`, templates, `target.toml`) em `ARCHITECTURE.md`. Além dos campos de lá, o `target.toml` aceita:

- `[[keys]]`: `file`, `group` (string ou lista para grupos aninhados), `key`, `value` | `delete = true` | `transform = "font-family"`;
- `[[states]]`: algo com comando de leitura e escrita. `get`, `set`, `restore` (opcional), `value`, `default` (usado no restore quando não havia valor) e `reapply_on_change`. O valor chega aos comandos em `$GIBI_VALUE`; escreva `$$GIBI_VALUE` no TOML, porque `$` sozinho é placeholder;
- `[[files]]` em `managed-block`: `comment` (`#`, `//`, `/*`, `;`) e `position` (`bottom`, `top`, `after-imports`);
- `[[files]]` em `copy`: `ignore`, lista de nomes que o próprio app cria no destino e que não contam como diferença (ex.: o `Cached Theme.pak` que o Brave grava na pasta do tema);
- `order` (ordem de execução) e `message` (texto mostrado quando o alvo muda algo);
- `generate`: script Python (relativo ao alvo) que roda antes do render e (re)escreve `templates/` a partir da paleta. Deve ser determinístico e só gravar o que mudou.
- `platforms`: `["linux"]` (padrão, quando o campo falta), `["windows"]` ou os dois. Alvo de outra plataforma é pulado sem erro;
- `[windows]`: tabela cujas chaves substituem as do topo quando roda no Windows (ex.: `brave` e `stylus` trocam `dest`, `message` e a detecção). Em `[[windows.files]]`, os `[[files]]` do Windows;
- `detect_paths`: lista de caminhos; o alvo é detectado se algum existir (sem shell). Substitui um `detect` herdado;
- `[[registry]]` (Windows): `key` (só `HKCU\...`), `name`, `type` (`dword`, `qword`, `string`, `expand_string`, `binary`), `value` | `delete = true`, e `format` para cores: `abgr`/`argb` (com `alpha` 0-255), `accent-palette` (os 32 bytes do `AccentPalette`) ou `shade:N` (o tom N dele, em ABGR);
- `[[fonts]]` (Windows): `family` (só para mensagens), `source` (URL ou caminho relativo ao alvo), `sha256` e `files` (glob dos arquivos de fonte dentro do `.zip`/`.tar.*`);
- `[[post]] notify = "<área>"` (Windows): `WM_SETTINGCHANGE` com essa área (ex.: `ImmersiveColorSet`), também no uninstall;
- `[windhawk]` (Windows, W2): `mod` (id do mod), `title` (nome exibido), `snippet` (onde gravar o YAML) e `[windhawk.settings]` com a configuração do mod em TOML, como no schema dele. Strings passam pelo render; as constantes do Windhawk (`$Bg`) se escrevem `$$Bg`;
- Placeholders só do Windows: `${user_data}` (`%LOCALAPPDATA%\gibi`), `${local_appdata}`, `${yasb_config}` e `${surface_float_opacity_hexalpha}` (a opacidade dos popups como alfa hex, para `#AARRGGBB`). Caminhos aceitam `%VAR%` no Windows.

## Licença

GPL-3.0-or-later. Ver `LICENSE`.

# Fase 1 — Fundação + todos os alvos exceto Kvantum

> Pré-requisito: ler `ARCHITECTURE.md` inteiro. Este arquivo diz **o que** construir nesta fase; as regras de paleta, estrutura, contratos e instalador estão lá e são obrigatórias.
>
> A fase 2 (Kvantum) vem depois, numa sessão separada. **Esta fase precisa deixar a porta pronta para ela** (ver seção 4).

## 0. Antes de começar

1. Confirme o ambiente: `plasmashell --version` (esperado Plasma 6), `echo $XDG_SESSION_TYPE`, `python3 --version` (>= 3.11 por causa do `tomllib`).
2. Para cada pacote citado abaixo, verifique se existe nos repositórios oficiais ou do CachyOS (`pacman -Si <pkg>`) antes de recorrer ao AUR (`paru -Si <pkg>`). Registre no `README.md` de onde cada dependência vem.
3. Trabalhe em commits pequenos, um por etapa abaixo.

## 1. Fundação (fazer primeiro, nada de alvo antes disso funcionar)

- `palette.toml` completo com todos os tokens de `ARCHITECTURE.md` §3.
- `tooling/` com os comandos `render`, `check`, `apply`, `restore`, e as flags `--only`, `--dry-run`, `--list`.
- Variantes de formato de cor (`_nohash`, `_rgb`, `_r/_g/_b`) conforme §4.2.
- Backup/restore com `manifest.json` conforme §5.2, incluindo valores antigos de chaves `kwriteconfig6`.
- Modo `managed-block` com delimitadores.
- Verificação de contraste conforme §5.3.
- `install.sh` e `uninstall.sh` finos.
- `README.md` com créditos à Cecilia May **no topo**, `LICENSE` GPL-3.0, `.gitignore` com `build/`.
- Um alvo de teste trivial (ex.: `targets/_selftest/`) que renderiza um arquivo para `/tmp` e prova: render, idempotência, dry-run, backup e restore.

Critério para seguir: `./install.sh --only _selftest` duas vezes seguidas não altera nada na segunda; `./uninstall.sh` restaura.

## 2. Alvos

### 2.1 `fonts`
- Pacotes: `inter-font`, `ttf-cascadia-code-nerd`.
- Aplicar via `kwrite` em `kdeglobals` (grupo `General`: `font`, `menuFont`, `toolBarFont`, `smallestReadableFont`; `fixed` com a mono). Tamanhos: manter os tamanhos atuais do usuário, trocar só a família.

### 2.2 `kde-colors`
- Template de color scheme do KDE (`.colors`) → `~/.local/share/color-schemes/Gibi.colors` (modo `copy`).
- Mapeamento principal:
  - `Colors:Window` / `Colors:View` BackgroundNormal = `base.100`; BackgroundAlternate = `base.110`.
  - `Colors:Button` BackgroundNormal = `base.120`.
  - `Colors:Header` e `Colors:Complementary` = `base.110` / `base.140`.
  - ForegroundNormal = `base.20`; ForegroundInactive = `base.40`; ForegroundActive = `base.10`.
  - `Colors:Selection` BackgroundNormal = `selection.bg`, ForegroundNormal = `selection.fg`.
  - **DecorationFocus = `accent.primary`** (anel de foco). DecorationHover = `base.70` (**não** amarelo, para não pintar hover grande de amarelo).
  - ForegroundLink = `sem.blue`; ForegroundVisited = `accent.secondary`; ForegroundNegative/Neutral/Positive = `sem.red`/`sem.orange`/`sem.green`.
  - `WM` activeBackground/inactiveBackground = `base.110`; activeForeground = `base.20`.
- Aplicar com `plasma-apply-colorscheme Gibi`.
- Cuidado com a regra 3.4.1: revise se alguma role do KDE usa DecorationFocus como preenchimento grande; se sim, documente.

### 2.3 `klassy`
- Pacote: `klassy` (verificar repo CachyOS, senão AUR).
- Via `kwrite`:
  - `kwinrc` → decoração de janela Klassy.
  - `kdeglobals` → `widgetStyle=Klassy` **nesta fase**.
  - `klassyrc` → sombras difusas (tamanho médio, força moderada, cor preta), cantos coerentes com `shape.radius_l`, barra de título usando cores do esquema.
- Usar só chaves que realmente existem na versão instalada: descubra-as lendo o `klassyrc` gerado após mudar opções na GUI ou a documentação do projeto. Não inventar chaves.

### 2.4 `blur`
- KWin: efeito `blur` habilitado, força baixa (`kwinrc`, grupo `Effect-blur`). Não habilitar blur/transparência em janelas normais.
- Painel do Plasma: translucidez ativada com opacidade próxima de `surface.float_opacity`.
- Menus e popups: usar a opção de translucidez de menus do Klassy **se existir**; se não existir, deixar opaco e anotar no `README` que isso fica para a fase 2 (o Kvantum tem controle de blur de popups).
- Não instalar plugins extras de blur.

### 2.5 `gtk`
- O KDE já gera `~/.config/gtk-3.0/colors.css` a partir do color scheme. **Não sobrescrever esse arquivo.**
- Criar `~/.config/gtk-3.0/gibi.css` e `~/.config/gtk-4.0/gibi.css` (symlink) com `@define-color` para os nomes usados por GTK3/libadwaita (`accent_bg_color`, `accent_fg_color`, `window_bg_color`, `view_bg_color`, `headerbar_bg_color`, `card_bg_color`, `popover_bg_color`, `window_fg_color` etc.) e raios de `shape`.
- Incluir via `managed-block` com `@import 'gibi.css';` no `gtk.css` de cada versão.
- `accent_bg_color` = `accent.primary`, `accent_fg_color` = `accent.on_primary`. Respeitar a regra 3.4.1: verificar em um app libadwaita (ex.: um app GNOME qualquer instalado) se algo grande fica amarelo; se ficar, sobrescrever o seletor específico.

### 2.6 `ghostty`
- Tema em `~/.config/ghostty/themes/gibi` (symlink).
- `background` = `base.100`, `foreground` = `base.20`, `cursor-color` = `accent.primary`, `cursor-text` = `accent.on_primary`, `selection-background` = `selection.bg`, `selection-foreground` = `selection.fg`.
- Paleta ANSI 0-15: preto = `base.140`/`base.70`, vermelho = `sem.red`, verde = `sem.green`, amarelo = `sem.yellow`, azul = `sem.blue`, **magenta = `accent.secondary`**, ciano = `sem.cyan`, branco = `base.20`/`base.10`. Variantes brilhantes podem ser levemente mais claras (calcular no template ou definir tokens próprios em `palette.toml`, nunca hex solto no template).
- `managed-block` no `~/.config/ghostty/config` com `theme = gibi` e `font-family = CaskaydiaCove Nerd Font`. Não tocar no resto do arquivo.

### 2.7 `icons`
- Pacotes: `papirus-icon-theme`, `papirus-folders`.
- Tema de ícones Papirus-Dark via `kwrite` (`kdeglobals` → `Icons/Theme`).
- Cor das pastas: padrão **`brown`**; documentar no README como trocar para `yellow` (`papirus-folders -C yellow --theme Papirus-Dark`). O `uninstall` volta para a cor padrão (`papirus-folders -D`).

### 2.8 `brave`
- Gerar em `build/brave-theme/` uma extensão de tema estilo Chrome (`manifest.json` com `manifest_version: 3` e bloco `theme.colors`): `frame`, `frame_inactive`, `toolbar`, `tab_text`, `tab_background_text`, `bookmark_text`, `ntp_background`, `ntp_text`, `omnibox_background`, `omnibox_text`, `button_background`.
- Mapeamento: frame = `base.110`, toolbar e aba ativa = `base.100`, textos = `base.20`/`base.40`, omnibox = `base.120`.
- **Não usar o amarelo em nenhuma superfície do Brave** (regra 3.4.1); o tema do Brave é só de cores planas.
- Instalação não é automatizável sem política gerenciada: copiar a pasta para `~/.local/share/gibi/brave-theme/` e imprimir as instruções (brave://extensions → modo desenvolvedor → carregar sem compactação).

### 2.9 `lookandfeel`
- Pacote Look-and-Feel em `~/.local/share/plasma/look-and-feel/org.gibi.desktop/` com `metadata.json` e `contents/defaults` apontando para: color scheme Gibi, decoração Klassy, widget style atual (Klassy nesta fase), ícones Papirus-Dark.
- **Sem layout de painéis/desktop** no pacote, para não resetar o layout do usuário.
- Aplicar com `plasma-apply-lookandfeel -a org.gibi.desktop`.
- Este é o último alvo a rodar no `install.sh`.

## 3. Critérios de aceite

- `./install.sh --dry-run` lista todas as mudanças sem tocar em nada.
- `./install.sh` em uma máquina limpa aplica tudo; rodar de novo não muda nada.
- `./uninstall.sh` volta ao Breeze e restaura arquivos e chaves anteriores.
- `python3 -m tooling check` passa.
- Nenhum hex solto em template: toda cor vem de `palette.toml`.
- `docs/CHECKLIST-FASE-1.md` gerado, cobrindo: Dolphin, Configurações do Sistema, Kate, um app GTK3, um app libadwaita, Ghostty (rodar um script de amostra da paleta ANSI), Brave, painel, um menu de contexto e uma notificação (`notify-send teste`).

## 4. Deixar pronto para a fase 2 (obrigatório)

- Tokens `shape.*` e `keycap.*` presentes e expostos no render, mesmo que pouco usados agora.
- Renderizador testado com um arquivo `.svg` de exemplo contendo placeholders (pode ficar em `targets/_selftest/`).
- `widgetStyle` definido em **um único lugar** (constante ou token), para que a fase 2 troque de `Klassy` para `kvantum` sem caçar ocorrências.
- O pacote Look-and-Feel lê o widget style dessa mesma fonte.
- Um `docs/PHASE-2-NOTES.md` curto com qualquer coisa que a fase 2 precise saber (limitações descobertas no Klassy, se menus ficaram opacos, etc.).

# Notas para a fase 2 (Kvantum)

Coisas que a fase 1 descobriu e que a fase 2 precisa saber.

## Troca do widget style

- Fonte única: `palette.toml → [kde].widget_style` (hoje `"Klassy"`). Trocar para `"kvantum"` propaga para:
  - `targets/klassy/target.toml` (chave `kdeglobals [KDE] widgetStyle = ${kde_widget_style}`);
  - `targets/lookandfeel/templates/package/contents/defaults` (`widgetStyle=${kde_widget_style}`).
- A chave fica em `[KDE]`, **não** em `[General]`, no Plasma 6.
- Depois da troca, o alvo `klassy` continua cuidando só da decoração. Vale mover a chave `widgetStyle` para um alvo neutro, ou para o próprio alvo `kvantum`, para o nome do alvo não enganar. Continue lendo o valor do token.
- Nesta máquina, o valor **anterior** à fase 1 era `widgetStyle=kvantum` com o tema Kvantum `ClaudePurple` (`~/.config/Kvantum/kvantum.kvconfig`). O backup da fase 1 guarda isso: se rodar `./uninstall.sh`, o Kvantum/ClaudePurple volta.
- Pacote instalado: `kvantum-qt6-git` (provê `kvantum`). Não há `kvantum-qt5`.

## Menus e popups

- Na fase 1, a translucidez dos menus vem do **Klassy**: `klassy/klassyrc [Style] MenuOpacity = ${surface_float_opacity_pct}` (88), no alvo `blur`. O blur atrás é o efeito `blur` do KWin (`BlurStrength = 3`, `NoiseStrength = 0`).
- Com o Kvantum desenhando os widgets, essa chave do Klassy deixa de ter efeito. **Remova-a do alvo `blur`** e configure a translucidez/blur de popups no `.kvconfig` (`translucent_windows=false`, blur só para menus/popups), para não duplicar.
- O efeito `blur` do KWin continua necessário (é ele quem desfoca).

## Painel

- O alvo `blur` só liga o modo `translucent` dos painéis (via script do plasmashell, `targets/blur/panel-opacity.sh`). O **nível** de translucidez vem do estilo do Plasma (Plasma Style), não dá para fixar em 0.88 sem um Plasma Style próprio (fora de escopo).

## Tokens e render

- `shape.*`, `keycap.*`, `focus.*`, `shade.*` e `surface.*` já estão expostos: `${keycap_base_depth}`, `${keycap_base_color}`, `${keycap_highlight}`, `${keycap_drop}`, `${keycap_disabled_opacity}`, `${focus_ring_width}`, `${focus_ring_opacity}`, `${shape_radius_m}` etc. Floats entre 0 e 1 também ganham `_pct` (ex.: `${surface_float_opacity_pct}` = 88).
- O renderizador trata `.svg`/`.kvconfig` como texto comum. Está testado em `targets/_selftest/templates/sample.svg` (`tests/selftest.sh`).
- **Atenção ao SVG do Kvantum:** tokens como `keycap.base_color` e `keycap.highlight` são `rgba(...)`. O QtSvg (SVG Tiny 1.2) não entende `rgba()` em `fill`, então no SVG é preciso separar cor e opacidade (`fill="#000000" fill-opacity="0.28"`). Sugestão: ensinar o `tooling/palette.py` a gerar variantes `${x_hex}` e `${x_alpha}` para valores `rgba(...)`. Assim nenhum literal escapa da paleta.
- Placeholder desconhecido é erro de render. Para um `$` literal no template, use `$$`.

## Tooling disponível para o alvo kvantum

- `[[files]]` com `mode = "symlink"` aceita diretório inteiro (ex.: `templates/Gibi` → `~/.config/Kvantum/Gibi`).
- Para `~/.config/Kvantum/kvantum.kvconfig` → `theme=Gibi`, use `[[keys]]` com `file = "~/.config/Kvantum/kvantum.kvconfig"`, `group = "General"`, `key = "theme"`. O `kwriteconfig6` edita esse INI e o backup guarda o valor antigo (`ClaudePurple` aqui).
- `[[states]]` (get/set/restore via shell, com `$$GIBI_VALUE`) servem para qualquer coisa que tenha comando de leitura e escrita.
- `reapply_on_change = true` num state força o `set` quando algum arquivo do alvo mudou (útil se o Kvantum precisar de "reaplicar" o tema).

## Limitações e observações da fase 1

- `DecorationFocus = accent.primary` (amarelo): no Breeze/Klassy e no Kirigami ele é usado em anéis/bordas de foco. Checkbox marcado, slider e barra de progresso usam `Highlight` (seleção, roxo). Hover usa `DecorationHover = base.70`. Se a fase 2 achar algum widget Qt pintando área grande com a cor de foco, trate no Kvantum.
- `base.60` (texto desabilitado) sobre `base.100` dá 2.14:1, abaixo dos 3:1 da §3.4. Não é par obrigatório da §5.3 (e o WCAG isenta texto desabilitado), então o `check` só avisa. Se a fase 2 usar `base.60` para algo que não seja desabilitado, clareie o token.
- O Klassy guarda `[Global] LookAndFeelSet` no `klassyrc`. Não vimos o Klassy reescrever as chaves do tema ao trocar de Look-and-Feel, mas se o segundo `./install.sh` reaplicar chaves do `klassyrc`, é isso.
- O Ghostty é um app libadwaita: a barra de abas dele segue o `gtk-4.0/gibi.css`.

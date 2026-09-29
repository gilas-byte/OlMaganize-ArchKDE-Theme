# Checklist visual — Fase 1

O Claude Code não vê a tela. Depois de `./install.sh`, **faça logout/login uma vez** (algumas apps só releem fonte e estilo na inicialização) e confira os itens abaixo. Para cada app, tire um screenshot:

```sh
spectacle -b -f -n -o ~/gibi-check-<app>.png
```

Regra de ouro (ARCHITECTURE.md §3.4): **nenhuma área maior que um botão pode ficar amarela** (`#FFEA00`). O amarelo só aparece em anel de foco, cursor do terminal e, no máximo, preenchimento de botão. Seleção é roxa-acinzentada (`#5E4E5F`), nunca amarela.

## Antes de tudo

- [ ] `./install.sh` rodou sem erro e o resumo mostra `aplicado` ou `sem mudanças` em todos os alvos.
- [ ] `./install.sh` de novo: **todos** os alvos em `sem mudanças`. Se algum reaplicar, alguma coisa está reescrevendo o config (anote qual).

## Dolphin — `gibi-check-dolphin.png`

- [ ] Fundo da janela e da lista marrom (`#2E261F`); painel lateral (Locais) um tom diferente.
- [ ] Texto bege; itens do painel lateral em bege mais apagado.
- [ ] Pastas marrons (ícones Papirus com pastas `brown`).
- [ ] Selecionar um arquivo: fundo roxo-acinzentado, texto claro. **Não** amarelo.
- [ ] Passar o mouse sobre itens: hover discreto (marrom mais claro), **não** amarelo.
- [ ] Barra de título com as cores do esquema, opaca, cantos arredondados e sombra difusa.
- [ ] Fonte da interface é Inter.

## Configurações do Sistema — `gibi-check-systemsettings.png`

- [ ] Cores > esquema **Gibi** selecionado.
- [ ] Ícones > **Gibi-Papirus-Dark** selecionado.
- [ ] Estilo das aplicações > **Klassy**. Decorações de janela > **Klassy**.
- [ ] Tema global (Look-and-Feel) > **Gibi** aparece na lista.
- [ ] Navegar com **Tab** entre controles: o anel de foco aparece em amarelo, fino.
- [ ] Botões, checkboxes e sliders: nenhum preenchimento grande amarelo. (Checkbox marcado e slider usam a cor de seleção, roxa.)

## Kate — `gibi-check-kate.png`

- [ ] Editor com fundo marrom e texto bege (o esquema de cores do editor segue o do sistema, se estiver no padrão).
- [ ] Selecionar texto: fundo roxo.
- [ ] Menus (Arquivo, Editar…): fundo levemente translúcido, com blur atrás.

## App GTK3 (Meld ou Lutris) — `gibi-check-gtk3.png`

- [ ] Tema Breeze-GTK com as cores do esquema: fundo marrom, texto bege.
- [ ] Seleção roxa. Botões com cantos de ~7px.

## App libadwaita (GNOME Tweaks, ProtonPlus ou `zenity --info --text teste`) — `gibi-check-libadwaita.png`

- [ ] Fundo da janela marrom, headerbar um tom diferente, cards levemente mais claros.
- [ ] **Procure amarelo grande**: botões "suggested-action" (ex.: Aplicar/OK) ficam amarelos com texto escuro. Isso é tamanho de botão e está ok. Se alguma barra, aba inteira, linha de lista ou sidebar ficar amarela, anote o app e a área (vai virar override no `gtk4.css`).
- [ ] Seleção de texto roxa.
- [ ] Switches ligados ficam amarelos (pequeno, ok).

## Ghostty — `gibi-check-ghostty.png`

Abra um terminal novo (ou `ctrl+shift+,` para recarregar) e rode:

```sh
~/Documents/gibi-theme/docs/ansi-sample.sh
```

- [ ] Fundo marrom, texto bege, cursor amarelo com caractere escuro por baixo.
- [ ] Magenta (5 e 13) é o roxo `#A58BC0`, não rosa.
- [ ] Amarelo ANSI (3) é o amarelo "envelhecido" `#F9CF51`, diferente do cursor.
- [ ] Fonte CaskaydiaCove Nerd Font; os ícones da última linha aparecem (não quadrados).
- [ ] Selecionar texto: fundo roxo.
- [ ] O Ghostty usa libadwaita: confira se a barra de abas/título **não** ficou amarela.
- [ ] Observação: seu `config.ghostty` tem `background-opacity = 0.8`, o que deixa o terminal translúcido. O tema não mexe nisso. Se quiser a "janela de papel" opaca, apague essa linha.

## Brave — `gibi-check-brave.png`

Carregue a extensão (instruções impressas pelo install; pasta `~/.local/share/gibi/brave-theme`).

- [ ] Moldura/abas inativas em marrom `base.110`, aba ativa e barra de ferramentas em `base.100`.
- [ ] Barra de endereço em marrom escuro (`base.120`), texto bege.
- [ ] Nova aba com fundo marrom.
- [ ] **Nenhum** amarelo em superfície do Brave.

## Painel — `gibi-check-panel.png`

- [ ] Painel translúcido com blur leve do que está atrás.
- [ ] Ícones e texto do painel legíveis.
- [ ] Hover em itens do gerenciador de tarefas: não amarelo.

## Menu de contexto — `gibi-check-menu.png`

Clique com o direito na área de trabalho e em um arquivo no Dolphin.

- [ ] Fundo levemente translúcido (88%) com blur.
- [ ] Item em hover: não amarelo.

## Notificação — `gibi-check-notify.png`

```sh
notify-send teste "notificação do tema"
```

- [ ] Fundo escuro com as cores do esquema, texto bege legível.

## Desfazer

- [ ] `./uninstall.sh` volta ao estado anterior (no seu caso: esquema ClaudePurple, LnF MacTahoe-Dark, widgetStyle kvantum, ícones Papirus-ClaudePurple, GTK Orchis-Purple-Dark, fontes Hack). Faça logout/login depois.

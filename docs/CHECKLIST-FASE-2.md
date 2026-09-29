# Checklist visual — Fase 2 (Kvantum)

O Claude Code não vê a tela. Depois de `./install.sh`, **feche e reabra os apps Qt** (ou faça logout/login) e confira os itens abaixo. Para cada app, tire um screenshot:

```sh
spectacle -b -f -n -o ~/gibi-check-<app>.png
```

Para menus e tooltips, que somem ao perder o foco, use atraso: `spectacle -b -f -n -d 3000 -o ~/gibi-check-<app>-menu.png` e abra o menu nesses 3 segundos.

Antes de abrir os apps, dá para ver o tema sem tocar no sistema: `python3 tests/kvantum-preview.py` gera `build/kvantum-preview.png` (todos os estados de botão, campos, check/radio, abas, lista, árvore, slider, progresso, scrollbar), `-foco-campo.png`, `-menu.png` e `-tooltip.png`.

Regra de ouro (ARCHITECTURE.md §3.4): **nenhuma área maior que um botão fica amarela**. Nesta fase o amarelo aparece só em: anel de foco, linha de 2px da aba ativa, borda e base do botão padrão.

## Antes de tudo

- [ ] `./install.sh` rodou sem erro; resumo com `kvantum aplicado`.
- [ ] `./install.sh` de novo: **todos** os alvos em `sem mudanças` (o `kvantum-qt5` pode aparecer como `pulado`, ver abaixo).
- [ ] `python3 tests/kvantum-check.py` termina com `Kvantum OK.`
- [ ] `kvantummanager` abre, a aba **Change/Delete Theme** lista **Gibi** como tema ativo, sem mensagem de erro. (Não use o botão de apagar tema nele: os arquivos são symlinks para `build/`.)
- [ ] Configurações do Sistema > Estilo das aplicações: **kvantum** selecionado.

## Botões — Kate (Configurações > Configurar o Kate…) e diálogos — `gibi-check-botoes.png`

Os 5 estados + o botão padrão:

- [ ] **Normal:** tecla marrom com linha de brilho fina no topo, borda escura e uma base mais escura de ~3px embaixo, com sombrinha curta.
- [ ] **Hover:** a face clareia um passo.
- [ ] **Pressionado** (segure o clique): face mais escura, sem a base e sem a sombra, 1px mais baixa. O texto **não** desce (limitação do Kvantum, ver README).
- [ ] **Marcado** (botão de alternar, ex.: botões de formatação na barra do Kate): face roxa-acinzentada, afundada.
- [ ] **Desabilitado:** plano, sem base nem sombra, texto apagado.
- [ ] **Botão padrão** num diálogo de confirmação (ex.: fechar o Kate com um documento não salvo, ou Dolphin > apagar arquivo): **borda e base amarelas**, texto bege em negrito. É o único botão com amarelo na tela.

## Foco por teclado — `gibi-check-foco.png`

- [ ] Em qualquer diálogo, aperte **Tab** algumas vezes: botões ganham anel amarelo de 2px (meio transparente) em volta da tecla.
- [ ] Campo de texto com foco: anel amarelo no lugar da borda.
- [ ] Combo com foco: mesmo anel.
- [ ] Checkbox/radio/aba com foco: anel amarelo fino em volta do rótulo.

## Dolphin — `gibi-check-dolphin.png`

- [ ] Arquivo selecionado: fundo roxo-acinzentado com borda interna e uma base um pouco mais escura embaixo (como a sidebar do Obsidian Primary). **Não** amarelo.
- [ ] Hover em itens: marrom um pouco mais claro.
- [ ] Barra de ferramentas: botões sem fundo; no hover aparecem como tecla.
- [ ] Barra de rolagem fina (pílula marrom), sem trilho visível; mais clara no hover.
- [ ] Menu de contexto (botão direito): fundo levemente translúcido, blur atrás, cantos arredondados, sombra suave; item em hover com fundo roxo escuro.
- [ ] Tooltip (pare o mouse sobre um botão da barra): fundo quase preto, texto bege, borda fina.
- [ ] Nenhuma área grande amarela.

## Campos, combos, check e radio — Configurações do Kate ou Dolphin > Configurar — `gibi-check-campos.png`

- [ ] Campo de texto: afundado (mais escuro que a janela), borda interna, linha escura fina no topo, **sem** base de tecla.
- [ ] Combo (lista suspensa): mesmo visual de campo, seta fina à direita.
- [ ] Checkbox desligado: quadradinho escuro com borda; **ligado: roxo com ✓ claro** (não amarelo).
- [ ] Radio ligado: círculo roxo com ponto claro.
- [ ] Spinbox: setinhas finas dentro do campo.

## Abas — Kate (várias abas abertas) ou Configurações do Dolphin — `gibi-check-abas.png`

- [ ] Aba ativa: fundo da janela com **linha amarela de 2px embaixo**.
- [ ] Abas inativas: um tom mais escuro, texto bege apagado; hover clareia.
- [ ] Botão de fechar aba: um ✕ fino.

## Slider e progresso — `gibi-check-slider.png`

- [ ] Slider (ex.: zoom na barra de status do Dolphin, ou volume no VLC): trilho escuro fino, parte preenchida roxa, alça redonda pequena com efeito de tecla.
- [ ] Barra de progresso (ex.: espaço livre na barra de status do Dolphin, ou copiando um arquivo grande): trilho escuro, preenchimento roxo, texto escuro legível sobre o roxo.

## Listas, árvores e cabeçalhos — Kate (painel de documentos/sistema de arquivos) — `gibi-check-listas.png`

- [ ] Setas de expandir finas (› fechado, ⌄ aberto).
- [ ] Cabeçalho de colunas (Dolphin em modo Detalhes): fundo um tom mais escuro, linha fina embaixo, separadores finos.

## Configurações do Sistema — `gibi-check-systemsettings.png`

- [ ] Grande parte é QML/Kirigami: o efeito de tecla pode aparecer incompleto ali (limitação conhecida). O que importa: cores certas e **nenhuma área grande amarela**.
- [ ] Diálogos de arquivo (Kate > Abrir): lista, campos e botões como acima.

## App Qt5 — VLC — `gibi-check-vlc.png`

Esta máquina tem Qt5 (`vlc-gui-qt`). Sem o plugin Qt5, o VLC ignora o Kvantum.

- [ ] Instale o plugin: `./install.sh --only kvantum-qt5` num terminal (pede confirmação e `sudo pacman -S kvantum-qt5`).
- [ ] Abra o VLC: botões de tecla, slider de volume/posição roxo, menus translúcidos.

## Se algo sair errado

- Voltar só os widgets para o Klassy da fase 1: `./uninstall.sh --only kvantum`.
- Voltar tudo ao estado de antes do tema: `./uninstall.sh`.
- Elemento cinza/estranho (fora da paleta): o Kvantum caiu no tema padrão dele porque falta um elemento no SVG. Anote o widget e o app; `tests/kvantum-check.py` cobre só os elementos referenciados no kvconfig.

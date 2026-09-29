# Checklist visual — Fase 3 (Plasma Style)

O Claude Code não vê a tela. O `./install.sh` já aplica o Plasma Style na hora (o plasmashell recarrega sozinho); se algo parecer velho, faça logout/login uma vez. Para cada item, tire um screenshot:

```sh
spectacle -b -f -n -o ~/gibi-check-<coisa>.png
```

Popups somem ao perder o foco: use atraso e abra o popup nesses 3 segundos:

```sh
spectacle -b -f -n -d 3000 -o ~/gibi-check-<coisa>.png
```

Antes de mexer no desktop, dá para ver o tema offscreen: `python3 tests/plasma-style-preview.py` gera `build/plasma-style-preview.png` com barra encostada e flutuante, tarefas nos estados, popup com cabeçalho e os controles do Plasma, renderizados pelo KSvg de verdade.

Regra de ouro (ARCHITECTURE.md §3.4): **nenhuma área maior que um botão fica amarela**. Nesta fase o amarelo aparece só em: anel de foco, linha de 2px da aba ativa e borda/base da tarefa que pede atenção.

## Antes de tudo

- [ ] `./install.sh` sem erro; resumo com `plasma-style aplicado`. Rodando de novo, tudo em `sem mudanças`.
- [ ] `python3 tests/plasma-style-check.py` termina com `Plasma Style OK.`
- [ ] Configurações do Sistema > Aparência e Estilo > Cores e Temas > **Estilo do Plasma**: **Gibi** selecionado, com miniatura, sem erro.

## Barras — `gibi-check-barras.png`

- [ ] Barra de cima e de baixo marrons, levemente translúcidas (dá para perceber o papel de parede borrado atrás), sem o visual do MacTahoe.
- [ ] Barra encostada na borda: linha fina mais clara só no lado voltado para a tela, cantos retos.
- [ ] Barra **flutuante** (editor de painel > Flutuante): cantos arredondados de 10px, borda nos 4 lados, sombra suave embaixo.
- [ ] Modo opaco (editor de painel > Opacidade > Opaco): marrom sólido, mesma forma.

## Tarefas — `gibi-check-tarefas.png`

- [ ] Apps abertos sem foco: ícone sem fundo, com uma barrinha bege na borda de baixo (na de cima, se a barra estiver em cima).
- [ ] Hover numa tarefa: aparece uma **tecla** marrom (brilho no topo, base escura embaixo, sombrinha).
- [ ] Janela ativa: tecla com face **marrom-dourada** e barrinha **amarela**, dá para distinguir do hover.
- [ ] Janela minimizada: sem fundo, barrinha mais apagada.
- [ ] Janela pedindo atenção (um app que "pisca" na barra, ex.: mensagem nova no Vesktop ou download terminado no Brave com a janela sem foco): tecla com **borda e base amarelas**.
- [ ] Tarefas agrupadas (várias janelas do mesmo app): selinho amarelo com "+".
- [ ] Barra de progresso na tarefa (copiar um arquivo grande no Dolphin): faixa amarela translúcida.

## Popups — `gibi-check-popups-*.png`

- [ ] Lançador (menu de aplicativos): fundo marrom levemente translúcido com blur atrás, cantos de 10px, borda fina, sombra suave. Campo de busca afundado; com o cursor dentro, anel amarelo fino.
- [ ] Cabeçalho do popup (topo do lançador, da bandeja): faixa um tom mais escura com linha fina embaixo.
- [ ] Bandeja do sistema (setinha ^): lista com hover discreto; switches (Wi-Fi, Bluetooth) **amarelos** quando ligados, alça redonda clara.
- [ ] Calendário do relógio: fundo igual aos outros popups. (O calendário em si segue o Breeze recolorido.)
- [ ] Volume: slider com trilho escuro, parte preenchida amarela, alça redonda de tecla.
- [ ] Notificação (`notify-send "Gibi" "teste de notificação"`): mesmo visual dos popups, **sem** amarelo.
- [ ] OSD (mudar o volume pelo teclado): mesmo visual.
- [ ] Botões dentro dos popups (ex.: "Configurar…" em qualquer popup): teclas pequenas com cantos de 4px.

## Dicas — `gibi-check-dica.png`

- [ ] Parar o mouse sobre um ícone da barra: dica quase preta (`base.140`), texto bege, borda fina, cantos de 4px.

## Controles do Plasma em configurações de widgets — `gibi-check-widget-config.png`

Botão direito num widget da barra > Configurar…:

- [ ] Checkbox desligado: tecla quadradinha; ligado: amarela com ✓ escuro. **Não** redonda (redondo é o radio).
- [ ] Radio ligado: círculo amarelo com ponto escuro.
- [ ] Abas (quando houver): aba ativa com linha amarela de 2px.

## Se algo sair errado

- Voltar só as barras e popups ao tema anterior (MacTahoe-Dark aqui): `./uninstall.sh --only plasma-style`.
- Elemento com cara de Breeze azul (fora da paleta): o Plasma caiu num arquivo que o Gibi não desenha e que tem cores fixas. Anote o widget; `tests/plasma-style-check.py` cobre só os arquivos que o Gibi fornece.
- Tema não atualiza depois de mudar a paleta: o cache do Plasma é por nome + versão (`~/.cache/plasma_theme_Gibi_v<versão>.kcache`) e a versão muda junto com a paleta. Se ainda assim ficar velho: `rm -f ~/.cache/plasma_theme_Gibi_v*.kcache && plasma-apply-desktoptheme Gibi`.

# Checklist visual — W1 (Windows: fundação segura, sem admin)

O Claude Code não vê a tela. O que dá para provar sem ela já está em `tests/selftest.ps1` (render, dry-run, idempotência, backup e restore de arquivos e registro, em pasta temporária e chave de teste) e em `tests/linux-invariants.py`. O que sobra está aqui, inclusive os três testes ao vivo que o spike S0 não pôde fazer (`docs/SPIKE-S0.md`). Para cada item, tire um screenshot:

```powershell
powershell -ExecutionPolicy Bypass -File .\tests\screenshot.ps1 -Name <app>            # tela inteira, em 3 s
powershell -ExecutionPolicy Bypass -File .\tests\screenshot.ps1 -Name <app> -Window    # só a janela em foco
```

O arquivo vai para `%USERPROFILE%\gibi-check-<app>.png`.

Regra de ouro (ARCHITECTURE.md §3.4): **nenhuma área grande amarela** e **nenhum roxo**. Fundo marrom (`#2E261F`), texto bege (`#D7C0A3`), amarelo vivo (`#FFEA00`) só em foco, cursor e detalhes.

## Antes de tudo

- [ ] `.\install.ps1 -DryRun` lista as mudanças sem erro (rodar com `powershell -ExecutionPolicy Bypass -File .\install.ps1 -DryRun`, ver README).
- [ ] `.\install.ps1` termina sem `erro:` no resumo. Rodando de novo: todos os alvos em `sem mudanças` e nenhum backup novo em `%LOCALAPPDATA%\gibi\state\backups`.
- [ ] `powershell -ExecutionPolicy Bypass -File .\tests\selftest.ps1` termina com `Selftest Windows OK.`
- [ ] Faça **logoff/login uma vez** depois do primeiro install (ver `win-colors` abaixo) e confira os itens de novo.

## `win-colors` (teste ao vivo pendente do S0)

- [ ] **Antes do logoff:** Configurações > Personalização > Cores mostra o destaque amarelo `#FFEA00`? Anote se sim, se não ou se ficou pela metade (ex.: Configurações amarelo, mas o Iniciar ainda dourado). É a resposta do spike S0 §2: o registro + `WM_SETTINGCHANGE` basta, ou precisa de logoff?
- [ ] **Depois do logoff:** destaque amarelo em Configurações > Cores, modo **Escuro** nos dois (apps e Windows).
- [ ] "Mostrar cor de destaque em Iniciar e na barra de tarefas" e "… nas barras de título e bordas das janelas" estão **desligados**. Barra de título de uma janela qualquer (Bloco de Notas, Explorer): **não** amarela.
- [ ] Onde o amarelo aparece: anel de foco/Tab em Configurações, botão principal de algum diálogo, toggle ligado, link. Tudo pontual (tamanho de botão, regra 3.4.1). Screenshot: `-Name settings-cores`.
- [ ] Texto sobre o amarelo (ex.: botão principal em Configurações) legível. O Windows escolhe preto ou branco sozinho; se escolher **branco**, anote (contraste ruim).
- [ ] Barra de tarefas nativa (se aparecer em algum monitor) e Iniciar: cinza/escuro, sem amarelo de fundo.

## `win-fonts` (teste ao vivo pendente do S0)

- [ ] Configurações > Personalização > Fontes: aparecem **Inter** e **CaskaydiaCove NF** (o Windows mostra o nome GDI, `NF`).
- [ ] Bloco de Notas > Formatar > Fonte: dá para escolher "Inter" com os pesos (Thin a Black) e "CaskaydiaCove NF".
- [ ] Ícones Nerd Font: no Windows Terminal, `Write-Host "$([char]0xE0A0) $([char]0xF07B) $([char]0xF489)"` mostra três ícones (ramo do git, pasta, terminal), não quadrados.

## `windows-terminal` (teste ao vivo pendente do S0)

Abra uma janela **nova** do Windows Terminal.

- [ ] **Sem aviso amarelo** de configuração no topo ("esquema de cores desconhecido" ou "fonte não encontrada"). Se aparecer, anote o texto exato.
- [ ] Windows PowerShell e Prompt de Comando: fundo marrom `#2E261F`, texto bege, cursor amarelo. Screenshot: `-Name terminal -Window`.
- [ ] Fonte: CaskaydiaCove (ligaduras `->` `=>` `!=` viram um glifo só).
- [ ] Rode a amostra ANSI e confira: vermelho, verde, amarelo-conteúdo (`#F9CF51`, não o vivo), azul, **magenta rosado** (`sem.pink`, nada de roxo), ciano:
  ```powershell
  0..15 | ForEach-Object { Write-Host -NoNewline "$([char]27)[38;5;${_}m cor $_ " }; Write-Host "$([char]27)[0m"
  ```
- [ ] Seleção de texto em marrom-dourado (`#6B592E`).
- [ ] Configurações do terminal > Perfis > Windows PowerShell > Aparência: esquema "Gibi" já selecionado. Transparência/acrílico continuam como você deixou.
- [ ] O `settings.json` **não** foi alterado: `Get-FileHash "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json"` igual ao de antes do install (anote o hash antes, se quiser).

## `yasb`

O YASB recarrega sozinho (`watch_stylesheet: True` no seu `config.yaml`).

- [ ] Barra: fundo marrom opaco, linha fina `#51402F` embaixo. Screenshot: `-Name yasb -Delay 0`.
- [ ] **Efeito de tecla** nos widgets (relógio, volume, wifi, clima, notas...): face um pouco mais clara que a barra, brilho de 1px no topo, base escura de 3px embaixo, cantos de 7px. É o item de maior risco (PHASE-WindowsOnly.md §4): o Qt pode desenhar mal borda de cores diferentes com raio. Se ficar quebrado (cantos serrilhados, base cortada, texto descentralizado), anote e eu simplifico.
- [ ] Hover num widget: face um passo mais clara.
- [ ] A barra de 30 px comporta as teclas (sem texto cortado em cima/embaixo).
- [ ] Workspaces do GlazeWM: ativo em amarelo vivo (só o texto), ocupados em bege apagado, vazios mais escuros. Sem tecla nos botões de workspace.
- [ ] Separadores (`|`) e bandeja sem tecla.
- [ ] Popups: calendário do relógio, menu de mídia, áudio, notas, clima, galeria de papéis de parede: fundo `#342C23`, borda marrom, texto bege.
- [ ] Tooltip (passe o mouse num widget): fundo bem escuro `#1C1712`, texto bege.
- [ ] Menu de contexto (botão direito na barra): item em hover marrom-dourado, checkbox marcado amarelo suave.
- [ ] Seu `styles.css` continua igual, exceto pelas 3 linhas do bloco `/* >>> gibi >>> */ … /* <<< gibi <<< */` no fim. O `config.yaml` não mudou.

## `brave` e `stylus`

- [ ] `brave://extensions` > Modo do desenvolvedor > Carregar sem compactação > `%LOCALAPPDATA%\gibi\brave-theme`: barra e abas marrons, sem amarelo. Screenshot: `-Name brave -Window`.
- [ ] Stylus > Gerenciar > Importar > `%LOCALAPPDATA%\gibi\stylus\import.json` (apague os "… Catppuccin" antes). Siga os sites de `docs/CHECKLIST-FASE-4.md`.

## Desinstalação

- [ ] `.\uninstall.ps1 -DryRun` lista o que restauraria: chaves com o valor antigo (destaque `0xFF00B9FF` = `#FFB900` nesta máquina), arquivos a remover, o bloco do `styles.css`.
- [ ] `.\uninstall.ps1`: destaque volta ao dourado anterior (talvez só depois de logoff), fragmento e `gibi.css` somem, `styles.css` volta byte a byte ao original, fontes saem de Configurações > Fontes.
- [ ] Se o uninstall disser que uma fonte "está em uso", feche o app (terminal, YASB) ou faça logoff e apague o arquivo indicado à mão.
- [ ] O tema do Brave e os estilos do Stylus continuam no navegador (o alvo não mexe nele): remova à mão se quiser.

# Checklist visual — W2 (stylers do Windhawk, sem admin)

Sem admin, o Windhawk não aceita configuração por script (`docs/SPIKE-S1.md`). O install gera um YAML por mod e você cola uma vez no "Textual mode". O que dá para provar sem a tela está em `tests/windhawk-check.py` (YAML, cores só da paleta, status) e em `tests/selftest.ps1` (snippets, exportação da configuração anterior, uninstall). Daqui para baixo é na tela. Screenshots como na W1:

```powershell
powershell -ExecutionPolicy Bypass -File .\tests\screenshot.ps1 -Name <app> [-Window]
```

Regra de ouro (ARCHITECTURE.md §3.4): **nenhuma área grande amarela**, **nenhum roxo**.

## Antes de tudo

- [ ] `.\install.ps1 -Only windhawk-start,windhawk-notifications,windhawk-explorer` sem erro. Cada alvo mostra uma linha `! pendente: ...` e o passo a passo.
- [ ] No Windhawk > Explorar, instale **Windows 11 Start Menu Styler** e **Windows 11 Notification Center Styler** (o File Explorer Styler você já tem).
- [ ] Para cada um dos três: rode o `Get-Content ... | Set-Clipboard` que o install mostrou, abra o mod > **Configurações** > **Textual mode**, selecione tudo, cole por cima e clique em **Salvar configurações**. Se o Windhawk acusar **"YAML Parse Error"**, anote a mensagem: é bug meu no gerador.
- [ ] Rode `.\install.ps1` de novo: os três alvos dizem `! Windhawk: o mod "..." já está com esta configuração` e o resumo fica sem "passo manual pendente". É a prova de que o colar pegou.

## Explorer (`windhawk-explorer`)

Abra uma janela **nova** do Explorer.

- [ ] Botões **minimizar, maximizar e fechar visíveis** no canto (a faixa das abas fica com a cor da moldura; pintá-la escondia esses botões).
- [ ] Aba ativa e barra de comandos em `#2E261F`, ligadas sem degrau. Linha fina `#51402F` embaixo da barra de comandos. Screenshot: `-Name explorer -Window`.
- [ ] Barra de endereço e busca: campo mais escuro (`#26211C`) com borda marrom e cantos de 7px.
- [ ] Início e Galeria (lado esquerdo > Início): fundo marrom.
- [ ] Dica (passe o mouse num botão da barra): fundo quase preto `#1C1712`, texto bege.
- [ ] **Esperado, não é bug:** a lista de arquivos e a árvore lateral continuam no escuro padrão do Windows (são Win32; ficam para a W3). Anote se o contraste entre o cabeçalho marrom e a lista escura incomoda.
- [ ] Sem acrílico/transparência (fundo opaco). Se a janela ficar preta onde antes havia efeito, anote: `backgroundTranslucentEffect: none` pode ter deixado alguma faixa sem pintar.

## Iniciar (`windhawk-start`)

- [ ] Painel do Iniciar em marrom `#342C23` levemente translúcido (blur), borda `#51402F`, cantos de 10px. Screenshot: `-Name iniciar -Delay 3` (abra o Iniciar durante a contagem).
- [ ] Caixa de busca como campo escuro com borda; nomes dos apps em bege, títulos ("Fixados", "Todos") em bege forte.
- [ ] Menu de botão direito num app fixado: fundo `#342C23`, borda marrom.
- [ ] Hover nos apps fixados: legível (o hover segue o padrão do Windows; anote se ficar estranho sobre o marrom).
- [ ] Pasta de apps fixados (se você usa): fundo marrom.
- [ ] Busca aberta pelo Iniciar: painel marrom.

## Central de notificações (`windhawk-notifications`)

- [ ] Win+N: central e calendário em marrom translúcido, borda marrom, cantos de 10px. Screenshot: `-Name central`.
- [ ] Win+A (configurações rápidas): painel marrom. Toggles ligados em amarelo (tamanho de botão, ok pela regra); o ícone sobre o amarelo legível.
- [ ] Controle de mídia (toque algo no navegador): painel marrom.
- [ ] Notificação (toast): provoque uma (um download concluído no Brave, ou um alarme de 1 minuto no app Relógio). Fundo marrom com borda.
- [ ] Jump list (botão direito num ícone da barra de tarefas, se a barra nativa aparecer em algum monitor): fundo marrom.

## Desinstalação

- [ ] `.\uninstall.ps1 -DryRun` mostra, para o Explorer, **"cole …\windhawk-windows-11-file-explorer-styler.yaml no mod … para voltar à configuração anterior"**. Esse arquivo tem a sua configuração `LiquidGlass`.
- [ ] `.\uninstall.ps1` apaga os YAML de `%LOCALAPPDATA%\gibi\windhawk`. **No Windhawk nada muda sozinho** (sem admin): cole o arquivo indicado no File Explorer Styler e, se quiser, desinstale os dois stylers novos pelo Windhawk.

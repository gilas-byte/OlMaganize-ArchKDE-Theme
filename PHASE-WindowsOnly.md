# Gibi para Windows: Arquitetura

> Complemento do `ARCHITECTURE.md` do repo `gilas-byte/OlMaganize-ArchKDE-Theme`. Leia aquele documento primeiro: paleta (§3), contrato de templates (§4.2), contrato de `target.toml` (§4.3), regras do instalador (§5) e regras de cor (§3.4) **continuam valendo**. Este arquivo só define o que muda no Windows.
> Máquina de referência: Windows 11 Pro **26H2, build 26300.9457** (pacote de habilitação sobre a base do 25H2).

## 1. Objetivo e escopo

Levar o tema Gibi para o Windows 11 com a maior fidelidade possível ao tema do KDE, **no mesmo repo, com o mesmo `palette.toml`**. Uso pessoal, uma máquina Windows do usuário (que também usa Arch).

- Instalação por um comando, idempotente, com backup e `uninstall`, igual ao Arch.
- Abordagem **agressiva, mas em camadas**: o que é seguro entra primeiro; o que mexe no sistema fica atrás de flag.
- A paleta, as regras de cor (sem roxo, amarelo pontual, WCAG AA) e os créditos do README (Primary, KvFlat, Breeze) são mantidos. Adicionar créditos a YASB e Windhawk onde houver derivação.
- O usuário já usa **YASB** (barra), **Windhawk** (bastante), **Windows Terminal** e **Raycast** (sem Pro).

## 2. Stack

| Camada | Escolha | Motivo |
| --- | --- | --- |
| Entrada | `install.ps1` / `uninstall.ps1` (PowerShell), finos | Equivalente ao `install.sh`; checam pré-requisitos e chamam `python -m tooling` |
| Lógica | Python 3.11+, **só stdlib** (`tomllib`, `winreg`, `string.Template`, `pathlib`, `shutil`, `subprocess`) | Mesmo núcleo do Arch; `winreg` é o equivalente do `kwriteconfig6` |
| Dependências | `winget` (com confirmação) | Equivalente ao `pacman` |
| Fonte da verdade | `palette.toml` (inalterado) | Uma paleta para tudo |
| Templates | `${token}` (inalterado) | Funciona para CSS, JSON, SVG |
| Estado/backup | `%LOCALAPPDATA%\gibi\state\` (backups, hashes de render) | Equivalente a `~/.local/state/gibi/` |

## 3. Estrutura do repositório (o que muda)

```
install.ps1 / uninstall.ps1        # novos; os .sh continuam para Linux
tooling/
  platform.py                      # detecta SO e build do Windows; filtra alvos
  backends/registry.py             # modo "registry": lê, grava e restaura chaves (winreg)
targets/<alvo>/target.toml         # ganha o campo: platforms = ["linux"] | ["windows"] | ambos
  # novos alvos Windows (ver §4):
  win-colors/  win-fonts/  windows-terminal/  yasb/
  windhawk-start/  windhawk-notifications/  windhawk-explorer/
  win-msstyles/  windhawk-uxtheme/        # tier agressivo
docs/
  CHECKLIST-W1.md  CHECKLIST-W2.md  CHECKLIST-W3.md
  SPIKE-S0.md  SPIKE-S1.md  SPIKE-S2.md
  RECOVERY-W3.md                          # obrigatório antes de liberar a W3
tests/                              # selftest equivalente para Windows (usa pasta temporária)
```

- O instalador **pula** alvos cujo `platforms` não inclui o SO atual (sem erro).
- Alvos reaproveitados sem mudança de lógica: `brave` e `stylus` (só ajustar caminhos).

## 4. Fases

### W1: fundação segura (sem admin)

| Alvo | O que faz |
| --- | --- |
| `win-colors` | Modo escuro (`AppsUseLightTheme`/`SystemUsesLightTheme` = 0 em `HKCU\...\Themes\Personalize`) e cor de destaque `#FFEA00`. Chaves exatas da cor de destaque: **confirmar no spike S0**. |
| `win-fonts` | Inter (UI) e CaskaydiaCove Nerd Font (mono), instaladas **por usuário**, sem admin. Origem (winget ou release oficial): decidir no spike S0. |
| `windows-terminal` | Esquema `gibi` (ANSI com `sem.*`, magenta = `sem.pink`, fundo `base.100`, texto `base.20`, cursor amarelo) e fonte mono. Não mexe em transparência/acrílico existentes. Mecanismo preferido: **fragmentos** do Windows Terminal (confirmar no S0). Fallback: bloco gerenciado no `settings.json`, editado **como texto** (o arquivo aceita comentários, então **não** usar `json.load`). Detectar Store, Preview e instalação sem pacote. |
| `yasb` | Gera `gibi.css`; adiciona só um `@import "gibi.css";` em bloco gerenciado no `styles.css` do usuário (`%USERPROFILE%\.config\yasb\`, ou `YASB_CONFIG_HOME` se definido). **Não toca no `config.yaml`.** O YASB recarrega sozinho, sem comando pós-install. |
| `brave`, `stylus` | Reaproveitados do Arch. |

Efeito de tecla no YASB (a validar visualmente): `border-top` de 1px clara (brilho) + `border-bottom` de 3px escura (base) + raio de `shape.radius_m`. O motor de CSS do YASB é próprio (Qt), então nem tudo do CSS3 vale. Se borda de cores diferentes com raio renderizar mal, simplificar e registrar em `docs/`.

### W2: stylers do Windhawk (sem admin)

- Alvos: `windhawk-start` (Start Menu Styler), `windhawk-notifications` (Notification Center Styler), `windhawk-explorer` (File Explorer Styler). O Taskbar Styler fica **desligado por padrão** (o usuário usa YASB).
- **Spike S1 primeiro:** descobrir se as configs dos mods podem ser aplicadas por script. Se sim, alvos gerenciados. Se não, o instalador gera os snippets em `build/windhawk/` e imprime um passo manual guiado.
- Esses alvos são **best effort**: falha vira aviso, nunca derruba o install (mods podem quebrar depois de updates do Windows).

### W3: tier agressivo (`-Aggressive`, exige admin)

Objetivo: efeito de tecla e cores nos controles Win32 (botões, abas, scrollbars, menus clássicos, partes do Explorer) via visual style de sistema.

1. **`win-msstyles`**: gerar um `.msstyles` **derivado do `aero.msstyles` local** do próprio Windows do usuário (formato do Windows 11, casado com o build dele). Substituir imagens (atlas PNG com margens, fatiados por `tooling/svgslice.py` e rasterizados) e cores a partir da paleta. **Nunca** redistribuir arquivo da Microsoft no repo.
2. **`windhawk-uxtheme`**: ativar o mod **UXTheme hook** do Windhawk (exige incluir `winlogon.exe` e `logonui.exe` na lista de processos do Windhawk) em vez do SecureUxTheme.
3. Opcional: mod de correção do DWM do Windhawk para cantos e sombras.
4. **Spike S2 primeiro:** descobrir se a edição do `.msstyles` pode ser automatizada (CLI/biblioteca) ou se é só GUI. Se for só GUI, o instalador gera os PNGs e o usuário importa uma vez no editor.

Salvaguardas obrigatórias da W3:
- Só roda com `-Aggressive`; pede UAC apenas para os passos que precisam.
- **Ponto de restauração** antes de aplicar.
- **Trava por build:** `tested_builds = [...]` no `target.toml`. Build fora da lista = recusa, a menos que `-ForceUntested`. O **26300 começa fora da lista**; o usuário testa e só então se acrescenta o build.
- `docs/RECOVERY-W3.md` (como se recuperar de login loop/tema quebrado) precisa existir **antes** de liberar a fase.
- `uninstall` volta ao tema padrão (aero) e remove o que o instalador criou, usando o manifest.

## 5. Spikes (experimentos curtos, resultado vira decisão)

| Spike | Pergunta | Se a resposta for "não" |
| --- | --- | --- |
| S0 (W1) | Fragmentos do Windows Terminal servem? Quais chaves do registro definem a cor de destaque? Como instalar fontes por usuário? | Bloco gerenciado no `settings.json`; escolher outro caminho para fontes |
| S1 (W2) | Dá para aplicar a config dos mods do Windhawk por script? | Gerar snippets + passo manual guiado |
| S2 (W3) | Dá para editar `.msstyles` por script? | Gerar PNGs + importação manual única |

Cada spike termina em `docs/SPIKE-Sx.md` com a conclusão. **Nenhum alvo da fase seguinte é implementado antes do spike dela.**

## 6. Instalador

```
.\install.ps1 [-DryRun] [-Only yasb,windows-terminal] [-List] [-Aggressive] [-ForceUntested]
.\uninstall.ps1 [-DryRun]
```

Mesmas regras do §5.2 do `ARCHITECTURE.md`, com estas adaptações:
- **Backup do registro:** valor antigo de cada chave vai para o `manifest.json`; `uninstall` restaura (ou apaga a chave, se não existia).
- **Sem admin** em W1 e W2. Admin só na W3.
- Modo `copy` por padrão no lugar de `symlink`: symlink no Windows costuma exigir admin ou modo desenvolvedor. A detecção de mudança usa o hash do conteúdo já existente no Arch.
- Verificação de contraste WCAG (`tooling check`) roda igual, como pré-condição do install.

## 7. Decisões e porquês

- **Mesmo repo, mesma paleta:** o núcleo é portável (Python stdlib roda no Windows). Renomear o repo (hoje "ArchKDE") é uma tarefa à parte; o GitHub redireciona o link antigo. Atualizar o §7 do `ARCHITECTURE.md` (Windows deixa de ser "fora de escopo").
- **Ordem W1 → W2 → W3:** do mais seguro ao mais arriscado. Se a W3 falhar, W1 e W2 continuam funcionando sozinhas.
- **UXTheme hook do Windhawk em vez de SecureUxTheme:** o SecureUxTheme declara suporte até a 24H2 (versões novas "não testadas") e o último commit é de junho/2025; o hook roda dentro do Windhawk (que o usuário já usa) e aplica sem reiniciar.
- **Derivar do `aero.msstyles` local:** o `aero.msstyles` do Windows 10 é só parcialmente compatível com o 11; o do próprio sistema já vem no formato certo. Evita redistribuir arquivo da Microsoft num repo GPL.
- **Ficar no 26H2:** o 26H2 é um pacote de habilitação (KB5121794) sobre a mesma base do 25H2, então o risco pros componentes de tema é provavelmente similar. Ainda assim, não há relatos de `.msstyles`/UXTheme hook no 26H2, e a janela de 10 dias de "voltar" provavelmente fecha antes da W3. A rede de segurança é ponto de restauração + trava por build.
- **Verificação visual:** o Claude Code não vê a tela. Cada fase gera `docs/CHECKLIST-W*.md` e um `tests/screenshot.ps1` (captura via PowerShell) para o usuário conferir.

## 8. Limitações conhecidas (expectativa honesta)

- **Apps WinUI** (Configurações, apps novos) **não** recebem o efeito de tecla nem o `.msstyles`. O efeito aparece em YASB, terminal, apps Win32 e partes do Explorer.
- **Moldura/barra de título** das janelas é desenhada pelo DWM; o resultado da W3 aí é incerto.
- **Explorer:** o styler do Windhawk provavelmente pega só a parte moderna (barra de comandos, navegação); o miolo Win32 depende do `.msstyles`.
- **Mods do Windhawk** podem exigir atualização após updates do Windows.
- A cor "papel" é o marrom "cartolina" escuro; **sem modo claro**.

## 9. Fora de escopo (por agora)

- **Raycast:** temas são exclusivos do Pro e o usuário não vai assinar. Se isso mudar, é "só mais um alvo" (gerar o JSON do Theme Studio a partir da paleta).
- Tema claro; macOS; Windows 10; Obsidian (continua com o Primary original).
- SecureUxTheme; Nilesoft Shell (menu de contexto); Rainmeter; ícones de pasta, cursor e sons.
- Taskbar nativa (o usuário usa YASB); Taskbar Styler só como opção futura.
- Rebaixar ou reinstalar o Windows.

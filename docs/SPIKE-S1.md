# Spike S1 (W2): dá para aplicar a configuração dos mods do Windhawk por script?

Pergunta do `PHASE-WindowsOnly.md` §5. Máquina: Windows 11 build 26300.9457, **Windhawk 1.7.3** instalado (não portátil). Tudo aqui foi lido sem gravar nada.

**Resposta: sem admin, não.** É o ramo "não" que a especificação já previa: o instalador gera os snippets em `build/windhawk/` e imprime um passo manual guiado. Achado que facilita: o Windhawk aceita **colar a configuração inteira como texto**, então o passo manual é um colar e salvar por mod.

## Onde a configuração mora

- `C:\Program Files\Windhawk\windhawk.ini`: `Portable=0`, `RegistryKey=HKLM\SOFTWARE\Windhawk`, `AppDataPath=%ProgramData%\Windhawk`.
- Configuração de cada mod: `HKLM\SOFTWARE\Windhawk\Engine\Mods\<mod-id>\Settings`, achatada em valores (`theme`, `controlStyles[0].target`, `controlStyles[0].styles[0]`, `styleConstants[0]`...). Ao lado, em `...\Mods\<mod-id>`, ficam `Disabled`, `Include`, `Version` e `SettingsChangeTime`, a marca que o Windhawk usa para perceber que a configuração mudou.
- **Permissão:** `...\Engine\Mods\<mod-id>` só pode ser gravada por Administradores, SYSTEM e CREATOR OWNER. O usuário comum só lê.
- `...\Engine\ModsWritable\<mod-id>` dá controle total a Everyone, mas é o armazenamento que o **próprio mod** usa em tempo de execução (`Wh_SetValue`), não a configuração. Gravar a configuração ali não tem efeito.
- O modo portátil (`Portable=1`) guardaria tudo em `.ini` dentro da pasta do Windhawk, e em `Program Files` isso também pede admin. Não é caminho.

Conclusão: automatizar significa gravar em HKLM, ou seja, **admin**, o que a especificação proíbe na W2 ("Sem admin em W1 e W2").

## O caminho sem admin

A interface do Windhawk 1.7.3 tem dois jeitos de colar a configuração inteira (textos conferidos nos arquivos de tradução da própria interface):

1. Mod > aba **Configurações** > botão **"Textual mode"** (sem tradução no pt-BR): editor YAML com a configuração inteira. Cola, **"Salvar configurações"**.
2. Mod > aba **Avançado** > **"Configurações de Mod"**: caixa com o JSON da configuração. **"Carregar"** mostra o atual, cola o novo, **"Salvar"**.

**Decisão:** os alvos da W2 geram, por mod, um `build/windhawk/<mod-id>.yaml`, para o modo textual, que é o mais legível. O install imprime o passo a passo e o caminho do arquivo. Também copia o arquivo para `%LOCALAPPDATA%\gibi\windhawk\`, para ficar num lugar fixo.

**Backup sem admin:** ler o HKLM é permitido. Antes de imprimir o passo manual, o alvo exporta a configuração **atual** de cada mod para o diretório de backup, no mesmo formato YAML. O uninstall não consegue gravar de volta, mas imprime o caminho desse arquivo para colar do mesmo jeito.

Os alvos são *best effort* (§W2): mod ausente ou formato inesperado vira aviso, nunca erro do install.

## Situação nesta máquina

| Mod | Instalado | Estado | Configuração atual |
|---|---|---|---|
| `windows-11-file-explorer-styler` | sim, 1.7 | ligado | tema pronto `LiquidGlass`, efeito `acrylicblur` |
| `windows-11-taskbar-styler` | sim, 1.10 | ligado | tema pronto `WindowGlass` |
| `windows-11-start-menu-styler` | **não** | | |
| `windows-11-notification-center-styler` | **não** | | |
| `dark-menus`, `taskbar-tray-system-icon-tweaks` | sim | ligados | fora do escopo do tema |

- Instalar mod também só pela interface (ou com admin). O passo manual inclui instalar os dois stylers que faltam.
- O Taskbar Styler continua fora do tema, como manda a especificação. A W2 não mexe nele.
- O File Explorer Styler já tem uma configuração sua (`LiquidGlass`). Colar a do Gibi **substitui** essa configuração inteira; o backup acima existe para poder voltar.

# Spike S0 (W1): Windows Terminal, cor de destaque, fontes por usuário

Perguntas do `PHASE-WindowsOnly.md` §5. Máquina: Windows 11 Pro build **26300.9457**, Windows Terminal **1.25.2733.0** (Store), YASB **2.0.7**, Python **3.12.10** por usuário (fora do PATH, ver "Achados extras").

**Resumo:** nenhum resultado contradiz a especificação. Fragmentos servem, as chaves de cor estão mapeadas, fontes por usuário funcionam sem admin. Os três **testes ao vivo** (gravar nas chaves reais, carregar um fragmento no terminal aberto, instalar uma fonte de verdade) **não foram feitos**: o primeiro foi barrado pela política de permissões desta sessão antes de rodar, e os outros dois mexeriam no sistema do mesmo jeito. Ficam como verificação no `CHECKLIST-W1.md`, depois do install de verdade, que já tem backup e uninstall.

## 1. Fragmentos do Windows Terminal: **servem**

Fonte: [JSON Fragment Extensions](https://learn.microsoft.com/en-us/windows/terminal/json-fragment-extensions) (atualizado em 2025-11).

- Pasta por usuário: `%LOCALAPPDATA%\Microsoft\Windows Terminal\Fragments\{app}\{arquivo}.json`. O terminal lê todos os `.json` da pasta. A pasta não existe nesta máquina; o instalador cria.
- É a mesma pasta para Store, Preview e instalação sem pacote: um fragmento só atende os três. A detecção só precisa saber se **algum** está instalado.
- Um fragmento pode **criar esquema de cores** (precisa de `name` e das 16 cores, `black` a `brightWhite`) e **alterar perfis existentes** com `"updates": "{guid}"`, mas só os perfis padrão (Prompt de Comando, Windows PowerShell) e os dinâmicos.
- Precedência: o fragmento entra como camada **abaixo** do `settings.json`. Se o usuário definir `colorScheme`/`font` no perfil ou em `profiles.defaults`, o valor dele vence. Hoje o `settings.json` desta máquina tem `"defaults": {}` e nenhum perfil define cor ou fonte, então o fragmento vale.
- O arquivo precisa ser UTF-8 (o tooling grava UTF-8).

**Decisão:** alvo `windows-terminal` = um arquivo `%LOCALAPPDATA%\Microsoft\Windows Terminal\Fragments\gibi\gibi.json` (modo `copy`) com:

- esquema `Gibi` (ANSI igual ao Ghostty: fundo `base.100`, texto `base.20`, cursor `accent.primary`, magenta `sem.pink`, brilhantes de `[ansi]`);
- `updates` nos dois perfis padrão (Windows PowerShell `{61c54bbd-c2c6-5271-96e7-009a87ff44bf}` e Prompt de Comando `{0caa0dad-35be-5f56-a8ff-afceeeaa6101}`) com `colorScheme` e `font.face`. Nada de opacidade, acrílico ou imagem de fundo.

O `settings.json` **não é tocado**, nem por bloco gerenciado. O fallback do bloco gerenciado (editar o JSONC como texto) não foi implementado: o terminal reescreve o `settings.json` inteiro quando você salva pela interface, então os marcadores sumiriam e o uninstall não acharia o bloco. Outros perfis (WSL, PowerShell 7, Azure) não recebem o esquema sozinhos: escolha "Gibi" neles pela interface, se quiser. Os GUIDs desses perfis variam por máquina, e `updates` para um GUID que não existe não está documentado.

**A verificar ao vivo (checklist):** o terminal abre com fundo marrom no Windows PowerShell e no Prompt de Comando, sem aviso de esquema ou fonte desconhecidos.

## 2. Cor de destaque: **chaves mapeadas, gravação ao vivo pendente**

Valores lidos nesta máquina (destaque atual `#FFB900`, modo escuro já ligado), conferidos com a cor efetiva via WinRT (`Windows.UI.ViewManagement.UISettings.GetColorValue`), que bateu byte a byte:

| Chave (HKCU) | Valor | Formato |
|---|---|---|
| `Software\Microsoft\Windows\CurrentVersion\Themes\Personalize` | `AppsUseLightTheme`, `SystemUsesLightTheme` | DWORD, 0 = escuro |
| idem | `ColorPrevalence` | DWORD: destaque no Iniciar e na barra de tarefas |
| `Software\Microsoft\Windows\DWM` | `AccentColor` | DWORD **ABGR** (`0xFF00B9FF` = `#FFB900`) |
| idem | `ColorizationColor`, `ColorizationAfterglow` | DWORD **ARGB** com alfa `0xC4` (`0xC4FFB900`) |
| idem | `ColorPrevalence` | DWORD: destaque nas barras de título |
| `Software\Microsoft\Windows\CurrentVersion\Explorer\Accent` | `AccentPalette` | BINARY de 32 bytes: 8 cores `R G B 00`. Ordem: Light3, Light2, Light1, **Accent**, Dark1, Dark2, Dark3, e uma oitava cor sem papel visível (aqui `#00B294`) |
| idem | `AccentColorMenu` | DWORD ABGR = Accent |
| idem | `StartColorMenu` | DWORD ABGR = Dark1 |

Tons que o Windows calculou para `#FFB900`: L1 `#FFC20D`, L2 `#FFD52A`, L3 `#FFE845`, D1 `#E19D00`, D2 `#9B5D00`, D3 `#5C2100`. O algoritmo não é documentado (ele também gira o matiz). Uma mistura simples com branco (15/30/45%) e preto (15/40/65%) chega perto: `#FFC426`, `#FFCE4C`, `#FFD873`, `#D99D00`, `#996F00`, `#594100`.

**Decisões:**

- `win-colors` grava as chaves acima com o backend `registry` (backup do valor antigo no `manifest.json`, uninstall restaura ou apaga) e depois manda `WM_SETTINGCHANGE` com `ImmersiveColorSet`, a mensagem que o Windows usa para avisar que a cor mudou.
- Tons do `AccentPalette` calculados a partir de `accent.primary` com a mistura acima, no código do backend (`format = "accent-palette"`). A oitava cor recebe o Dark3, para não aparecer teal.
- **`ColorPrevalence = 0` nas duas chaves** (Iniciar/barra de tarefas e barras de título). Com destaque `#FFEA00`, ligar qualquer uma das duas pintaria uma área grande de amarelo, o que fere a regra 3.4.1. Nesta máquina as duas já estão em 0.
- O `palette.toml` **não ganhou seção nova**. O gerador do Plasma Style põe um hash dos bytes do `palette.toml` na versão do tema, então qualquer byte a mais nele mudaria o `metadata.json` versionado e faria o Linux reaplicar o Plasma Style. Os tons derivados ficam no código, como os filtros do Stylus.

**Não verificado (o teste foi barrado antes de rodar):** se o Windows aplica a cor nova só com registro + `WM_SETTINGCHANGE`, ou se precisa de logoff, de reiniciar o Explorer ou da API não documentada `SetUserColorPreference` (uxtheme). O roteiro do teste está em `tests/win-accent-probe.ps1`: backup, gravação, leitura da cor efetiva num processo novo, restauração. Se o registro sozinho não bastar, o checklist manda fazer logoff uma vez. Usar a API não documentada fica como decisão sua, para uma W1.1.

## 3. Fontes por usuário: **funciona sem admin; origem = releases oficiais**

- Mecanismo (Windows 10 1809+): copiar o arquivo para `%LOCALAPPDATA%\Microsoft\Windows\Fonts\` e criar o valor `"<nome completo> (TrueType)" = <caminho completo>` em `HKCU\Software\Microsoft\Windows NT\CurrentVersion\Fonts`. Nesta máquina já existem 32 fontes instaladas assim (ex.: `JetBrainsMonoNerdFont-Italic (TrueType)`), no mesmo formato. Para a sessão atual ver a fonte sem logoff: `AddFontResourceW` + broadcast de `WM_FONTCHANGE` (via `ctypes`). No uninstall: `RemoveFontResourceW` antes de apagar o arquivo.
- Situação atual: nenhuma das duas está instalada. Existe só a `Cascadia Code`/`Cascadia Mono` sem ícones (vem com o Windows Terminal).
- **winget não serve:** não há pacote do Inter nem da CaskaydiaCove Nerd Font. O `winget font` é experimental (precisa ligar uma flag) e não foi considerado.
- **Origem decidida:** releases oficiais do GitHub, com versão e SHA-256 fixados no `target.toml`, baixados com `urllib` (stdlib) para `%LOCALAPPDATA%\gibi\cache\fonts\`:
  - Inter **v4.1**: `Inter-4.1.zip`, sha256 `9883fdd4a49d4fb66bd8177ba6625ef9a64aa45899767dde3d36aa425756b11e` (calculado aqui; o release não publica hash). Arquivos: os 18 TTF estáticos `extras/ttf/Inter-*.ttf` (sem `InterDisplay`). TTF estático em vez do variável porque apps GDI só enxergam os pesos nomeados.
  - Nerd Fonts **v3.5.1**: `CascadiaCode.tar.xz` (3,6 MB, em vez do `.zip` de 56 MB), sha256 `ae598e9401e2846aa3ee364513715de0490b844a4b54f0768991f45f23aa8369` (igual ao `digest` publicado pelo GitHub). Arquivos: os 12 `CaskaydiaCoveNerdFont-*.ttf` (sem `Mono`/`Propo`). O `tarfile` da stdlib abre `.tar.xz`.

**Achado: nome de família.** Na Nerd Font v3 o nome de família GDI (name ID 1) é **`CaskaydiaCove NF`**. `CaskaydiaCove Nerd Font` (o `font.mono` do `palette.toml`) é só o nome tipográfico (ID 16). O Windows Terminal usa DirectWrite, que acha o nome tipográfico, então o fragmento usa `${font_mono}` igual ao Linux. Apps GDI (e Qt em modo GDI) só acham `CaskaydiaCove NF`. O Inter não tem esse problema (ID 1 = `Inter` no Regular). **A verificar ao vivo:** o terminal não avisa "fonte não encontrada".

## Resultado ao vivo (install real, 2026-10-04)

Feito com `.\install.ps1` depois do spike, com backup em `%LOCALAPPDATA%\gibi\state\backups\`.

- **Cor de destaque: registro + `WM_SETTINGCHANGE` basta**, pelo menos para o que o WinRT reporta: num processo novo, sem logoff, `UISettings` deu Accent `#FFEA00`, AccentLight2 `#FFF04C`, AccentDark1 `#D9C700` (os tons calculados pelo alvo). Se o Explorer, o Iniciar ou apps já abertos acompanham sem logoff, só o checklist diz.
- **Fontes:** as 30 entraram em HKCU, e o .NET (GDI) já lista `Inter` e `CaskaydiaCove NF` na mesma sessão, sem logoff.
- **Windows Terminal:** fragmento gravado, `settings.json` com o mesmo SHA-256 de antes. **Mas o fundo continuou preto:** o terminal aberto desde antes do install não relê fragmentos, e janelas ou abas novas reaproveitam o mesmo processo. Amostrando um pixel do fundo: `#0C0C0C`; depois de atualizar só a data de modificação do `settings.json` (o terminal recarrega quando o arquivo muda): `#2E261F`. O alvo passou a fazer isso sozinho (`[[post]] notify = "windows-terminal"`, repetido no uninstall), sem mudar o conteúdo do arquivo.
- **YASB:** o watcher registrou `Stylesheet modified` logo depois do install (recarregou sozinho).
- Segunda execução: todos os alvos em `sem mudanças`, nenhum backup novo.

## Achados extras

- **Python fora do PATH.** `python` no PATH é só o atalho da Microsoft Store. Existe `%LOCALAPPDATA%\Programs\Python\Python312\python.exe` (3.12.10) e o `py.exe` em `...\Python\Launcher\`, também fora do PATH. O `install.ps1` procura nessa ordem: `py -3`, `python` (ignorando o atalho da Store), `%LOCALAPPDATA%\Programs\Python\Python3*\python.exe`.
- **Encoding.** O Python no Windows lê e grava texto em cp1252 por padrão, e os templates são UTF-8. O `install.ps1` liga `PYTHONUTF8=1`, e o tooling recusa rodar no Windows sem o modo UTF-8 (em vez de gravar arquivo errado).
- **CRLF.** O repo está com `core.autocrlf=true`, então os templates chegam aqui com CRLF. Rodar o render de alvos Linux no Windows muda o hash do Plasma Style (`metadata.json` versionado). Por isso o render passa a respeitar `platforms`: no Windows só os alvos Windows são renderizados.
- **YASB 2.0.7** (código em `C:\Program Files\YASB\lib\library.zip`, lido só pelas strings): o `CSSProcessor` resolve `@import "x";` **no lugar onde ele aparece** (inline), junta as variáveis de todos os `:root` e o watcher recarrega quando um arquivo **importado** muda. Por isso o bloco gerenciado com o `@import` vai no **fim** do `styles.css`: assim as regras do `gibi.css` vêm depois das suas e vencem. Seu `styles.css` é o tema "i3-style" do YASB, todo em variáveis (`--bar_bg`, `--text`, `--widget_bg`...). O `gibi.css` redefine essas variáveis e as `--yasb-*` do estilo novo do assistente do YASB, e acrescenta o efeito de tecla nos widgets. A barra está sem blur (`blur_effect.enabled: False`), então o fundo do Gibi é opaco.
- **Brave** instalado para todas as contas (`C:\Program Files\BraveSoftware\...`). Os arquivos do tema vão para `%LOCALAPPDATA%\gibi\` (`brave-theme\`, `stylus\import.json`).
- **Quebra de linha dos seus arquivos:** o `styles.css` usa LF. O bloco gerenciado no Windows preserva o tipo de quebra de linha do arquivo (não converte para CRLF).

# PHASE-4 — Alvo `stylus` (páginas web no marrom cartolina)

Plano para o Claude Code implementar. Antes de escrever qualquer coisa, leia `ARCHITECTURE.md`, `PHASE-1.md` a `PHASE-3.md` e um alvo existente parecido (`targets/brave/` e `targets/kvantum/generate.py`). Este alvo segue o **mesmo contrato** deles: `target.toml`, `templates/` com `${token}`, script `generate`, idempotência, sem sudo, `uninstall` que restaura, self-test.

Comentários de código em inglês. Python só com stdlib (o tooling não ganha dependências).

## 1. Objetivo

Levar o Gibi para o conteúdo das páginas no Brave, via extensão **Stylus**, reaproveitando os userstyles do Catppuccin (MIT) em vez de reescrever cada site.

O truque: os 134 userstyles do Catppuccin não têm cor própria. Todos importam uma lib compartilhada (`lib/std/v1.less`) que define 26 cores **por nome** (`@base`, `@text`, `@red`...). Se trocarmos os valores dessa lib pelos do Gibi, os 134 estilos são recoloridos de uma vez. O `palette.toml` continua sendo a fonte única.

**Fora de escopo (decidido com o Gilas):**

- Modo claro. Só dark, marrom "cartolina".
- Roxo em qualquer lugar. Só amarelo e marrom.
- Retocar cada site à mão (só os 3 que quebram, ver §6).
- Firefox `userContent.css`, mobile.

## 2. Resultado esperado

`./install.sh --only stylus` gera `~/.local/share/gibi/stylus/import.json`, no mesmo espírito do alvo `brave`: o usuário importa manualmente no Stylus (**Manage → Import**). Não há como instalar userstyles sem a UI do Stylus, e o alvo não tenta.

O `post message` do alvo deve avisar: **apague ou desative os estilos "… Catppuccin" antes de importar**, senão os dois ficam ativos em cada site e brigam.

## 3. Dependência upstream

- Upstream: `catppuccin/userstyles` (MIT, "Catppuccin Org"). O `import.json` atual do Gilas vem dele.
- Fixar num commit: `git submodule` em `vendor/catppuccin-userstyles/` (preferido, funciona offline) e registrar o SHA em `targets/stylus/UPSTREAM`. O zip que o Gilas tem é o `main` sem `.git`; use o `main` atual.
- Não copiar os estilos para o repo. O gerador lê do submodule.
- Crédito no topo do README, junto aos outros: Catppuccin userstyles, MIT, com o texto da licença preservado em `targets/stylus/LICENSE-catppuccin-userstyles`.

## 4. Pipeline do `generate.py`

Determinístico (sem timestamp, ordem fixa, seed fixa), só regrava o que mudou, como os outros geradores.

1. **Renderizar a lib** a partir do `palette.toml` (§5): um flavor único chamado `gibi`.
2. **Calcular os filtros CSS** de cada cor (§7).
3. **Reescrever o header** de cada `styles/*/catppuccin.user.less` (§8).
4. **Embutir a lib** dentro de cada estilo (§9).
5. **Aplicar o alias de flavors legados** (§6).
6. **Relatório de hex literais** (§10).
7. **Montar o `import.json`** (§11).

## 5. Mapeamento dos 26 slots

Valores em `palette.toml`, nada de hex solto nos templates. Os slots novos vão numa seção nova `[web]`, com valores `fn(...)` derivados de tokens que já existem, o que respeita a regra "sem hex novo".

**Convenção do `mix(a, b, t)`:** `t` é o peso da segunda cor (é como `selection.bg` já funciona). Confirme no `tooling` antes de usar; os hex abaixo assumem isso.

### Neutras (12 slots, quase 1:1 com `base.*`)

| slot | token | contraste sobre `base.100` |
|---|---|---|
| crust | `base.140` | 1.20 |
| mantle | `base.120` | 1.07 |
| **base** | `base.100` | fundo da página |
| surface0 | `base.90` | 1.08 |
| surface1 | `base.80` | 1.16 |
| surface2 | `base.70` | 1.50 |
| overlay0 | `base.60` | 2.14 |
| overlay1 | `base.50` | 3.60 |
| overlay2 | `base.40` | 4.96 |
| subtext0 | `mix(base.40, base.20, 0.5)` (novo, `[web]`) | 6.53 |
| subtext1 | `base.20` | 8.46 |
| text | `base.10` | 10.88 |

`base.110` fica sem uso.

### Cromáticas (14 slots)

| slot | valor | hex aproximado | contraste |
|---|---|---|---|
| red | `sem.red` | #E4574E | 4.08 |
| maroon | `mix(sem.red, sem.pink, 0.35)` | #E35E63 | 4.28 |
| peach | `sem.orange` | #EEA359 | 7.09 |
| yellow | `sem.yellow` | #F9CF51 | 9.96 |
| green | `sem.green` | #64C271 | 6.72 |
| teal | `mix(sem.green, sem.cyan, 0.5)` | #60B894 | 6.21 |
| sky | `mix(sem.cyan, base.10, 0.25)` | #7FBABB | 6.82 |
| sapphire | `mix(sem.cyan, sem.blue, 0.5)` | #5FA6BC | 5.43 |
| blue | `sem.blue` | #639CC0 | 4.99 |
| pink | `sem.pink` | #E06C8A | 4.73 |
| flamingo | `mix(sem.pink, base.10, 0.30)` | #E38D9C | 6.05 |
| rosewater | `mix(sem.pink, base.10, 0.55)` | #E6A8AB | 7.47 |
| **mauve** | `accent.secondary` | #F9CF51 | 9.96 |
| **lavender** | `base.40` | #AB916D | 4.96 |

`mauve` e `lavender` **não são roxos**. Os estilos referenciam esses nomes, então precisam ter valor; o Gilas não quer roxo, então mauve = amarelo suave e lavender = tan. Nomes iguais aos do Catppuccin, valores nossos.

### Regras do mapeamento

- **Manter todos os nomes idênticos** aos da lib original: `@rosewater`…`@crust`, `@accent`, os `@<nome>-filter`, `@accent-filter`, os mixins `.palette()`, `.defaults()`, `.rgbify()`, `.hslify()`, `.css-variables()` e as variáveis `--ctp-*`. Nome é API: vários estilos importam CSS de syntax highlight (highlight.js, pygments, prism) que lê `--ctp-*`. Só os valores mudam.
- **Accent:** o mapa ganha uma chave extra `@primary` = `accent.primary` (`#FFEA00`).
  - Padrão: `yellow` (`#F9CF51`, igual ao que Kvantum e Plasma Style já usam em checkbox e switch ligados).
  - O vivo fica como opção "Amarelo vivo".
  - Lista de opções sugerida: `yellow*`, `primary`, `peach`, `rosewater`, `flamingo`, `pink`, `red`, `green`, `teal`, `sky`, `blue`, `subtext0` (Gray). **Sem `mauve` e sem `lavender`** na lista.
- **Texto sobre accent:** `on_primary` (`#1C1712`) dá ~11.9:1 sobre `#F9CF51`.
- **`.defaults()`:** manter `color-scheme` como `dark` fixo, e a seleção de texto em `fade(@accent, 30%)`.

## 6. Flavors legados

Prototipei a troca de lib com uma paleta provisória: **131 dos 134 estilos compilaram**. Os 3 que quebram citam flavor direto:

- `chess.com`: `@catppuccin[@mocha][@text]` etc. (casas do tabuleiro)
- `google-photos` e `listenbrainz`: `@latte` dentro de `if(...)`

Cinco estilos (esses 3 mais `ichi.moe`, `pythonanywhere` e `twitter`) comparam `@flavor = latte`. Com flavor único isso cai sempre no ramo dark, o que é o desejado.

**Solução preferida:** no mapa da lib, definir `latte`, `frappe`, `macchiato` e `mocha` como **aliases** do `gibi`, sem tocar nos estilos. Se o Less não aceitar alias de mapa (não testei), gerar as quatro chaves com o mesmo conteúdo. Aceite: **134/134 compilam**.

## 7. Filtros CSS (obrigatório)

A lib tem um segundo mapa, `@catppuccin-filters`, com uma cadeia `brightness(0) saturate(100%) invert() sepia() saturate() hue-rotate() brightness() contrast()` para cada cor. Serve para recolorir ícones e SVGs pretos. O CSS compilado tem centenas de `filter:` e, sem recalcular, eles ficam com as cores do Mocha.

- Implementar um solver em Python (SPSA, como o "CSS filter generator" conhecido) que, para cada cor do mapa (26 + `primary`), acha a cadeia que aproxima o hex.
- Determinístico: seed fixa, número fixo de iterações.
- Guardar a perda de cada cor; o `tooling check` **falha** se alguma passar de um limite (definir com base no resultado real, e registrar no `docs/`).
- O prefixo `brightness(0) saturate(100%) invert(...)` é igual ao da lib original, siga-o.

## 8. Header de cada estilo

Regex simples serve: o formato é regular.

- **Os 3 `@var`**:
  - `lightFlavor` e `darkFlavor` viram select de **uma opção só**: `["gibi:Gibi*"]`. Assim o Stylus continua injetando as variáveis e o corpo do estilo não muda, e o modo claro do sistema também resolve para `gibi`.
  - `accentColor` usa a lista do §5.
- **Sem `@updateURL`** (nem `updateUrl` no JSON). Se o `updateUrl` do Catppuccin ficasse, o Stylus, que checa a cada 24h, **sobrescreveria o estilo gerado** com o original.
- `@name` = `"<site> Gibi"`; `@namespace` = `github.com/gilas-byte/gibi/styles/<site>` (nome distinto do Catppuccin para não colidir com os que já estão instalados).
- `@author` mantém o crédito ao Catppuccin, ex.: `Gibi (baseado em Catppuccin Userstyles)`.
- Manter `@version`, `@license MIT` e `@preprocessor less`.
- Variáveis específicas de cada site (checkbox, range, text) ficam **intactas**.

## 9. Embutir a lib

Substituir `@import "https://userstyles.catppuccin.com/lib/std/v1.less";` pelo conteúdo da lib gerada. Sem hospedagem, sem rede, sem estilo carregando de um servidor que não é nosso.

- Conferir se algum estilo importa `lib/mediawiki/v1.less`. Se sim, embutir também (aplicando a mesma paleta, se ela referenciar cores).
- Os `@import url(...)` de CSS de syntax highlight (`unpkg.com/@catppuccin/highlightjs`, `python.catppuccin.com/pygments`, `prismjs.catppuccin.com`) **ficam como estão**: são CSS puro que lê `--ctp-*`, então já acompanham a nossa paleta. Dependem de rede em tempo de uso, o que é aceitável; documentar em "Limitações conhecidas".

## 10. Relatório de hex literais

Os estilos têm cores escritas à mão no código, que **não passam pela lib** e vão aparecer pastel no meio do marrom. Medido no upstream: **444 hex literais em 58 estilos** (273 coloridos, 171 neutros), fora de `url()` e comentários. Piores: `tldraw` (86), `github` (43), `proton` (38), `twitter` (28), `duckduckgo` (22), `seventv` (19).

- Gerar `build/stylus-report.md` listando estilo, linha e hex, separado por coloridos e neutros.
- **Só relatar.** Não remapear automaticamente (risco de quebrar SVG e gradiente de forma silenciosa).
- Retoques manuais por site ficam para a Fase 4.1, guiados pelos sites que o Gilas realmente usa.
- Ignorar `darken()`, `lighten()`, `fade()`, `mix()`, etc. sobre variáveis da paleta: acompanham a troca sozinhos (~1667 chamadas no upstream).

## 11. Montagem do `import.json`

Espelhar `scripts/stylus-import/main.ts` do upstream:

```
[ { settings: { updateInterval: 24, updateOnlyEnabled: true, patchCsp: true, "editor.linter": "" } },
  { enabled: true, name, description, author, url, updateUrl?, usercssData: <metadata>, sourceCode, originalDigest } ... ]
```

- `usercssData` é o header parseado (`name`, `namespace`, `version`, `description`, `author`, `license`, `preprocessor`, `vars` com `type`, `label`, `name`, `value: null`, `default`, `options`). Use o `import.json` atual do Gilas como referência de formato: ele já tem um exemplo de cada tipo de `@var`.
- **`originalDigest` (não verificado):** o upstream o calcula com uma função do próprio Stylus. Não sei se o Stylus exige o campo na importação. Testar primeiro **sem** ele. Se a importação falhar ou os estilos não aparecerem, portar `calcStyleDigest` do Stylus para Python.
- Ordem alfabética por nome, `json.dumps` estável.
- **`enabled: true`** em todos por padrão. Se importar os 134 for exagero, `palette.toml [stylus] include = [...]` como lista opcional de sites (vazia = todos).

## 12. Verificações (`tests/`)

- `tests/stylus-check.py` (sem depender de node):
  - a lib gerada tem **todos os nomes** da lib original (superconjunto);
  - nenhum hex solto nos templates do alvo;
  - nenhum `@updateURL` nos estilos gerados;
  - os selects de flavor têm uma opção só;
  - contraste dos slots cromáticos ≥ 4.5:1 sobre `base.100`. O `overlay0` (2.14:1) entra como **aviso conhecido**, igual ao `base.60`. Ele é usado como cor de texto em ~27 dos 362 usos, então o relatório deve listar esses estilos.
- **Teste opcional com node** (roda só se `node` e `less` existirem, senão pula com aviso): compila os 134 com a lib gerada, com `lightFlavor=darkFlavor=gibi` e os defaults das demais variáveis injetados como o Stylus faz (select → valor da opção; checkbox → 0/1; text → string entre aspas). Aceite: **134/134**. Prototipei esse harness e ele reproduziu o resultado do upstream (134/134 com a lib original).
- `tests/selftest.sh`: incluir o alvo (render, dry-run, idempotência, restore).
- Idempotência: rodar duas vezes seguidas não muda nenhum byte em `~/.local/share/gibi/stylus/`.

## 13. Instalação e desinstalação

- Sem backup a fazer (o alvo só escreve em `~/.local/share/gibi/stylus/`). O `uninstall` remove a pasta.
- `post message` do install: caminho do arquivo, o aviso do §2 e, se possível, o total de estilos.
- `docs/CHECKLIST-FASE-4.md`: importar no Brave e conferir, em sites reais, que o fundo é o marrom, o accent é o amarelo suave, **não sobrou nenhum lilás**, blocos de código legíveis e ícones recoloridos. Sugestão: GitHub, YouTube, Arch Wiki, Wikipedia, Google, Stack Overflow, `claude.ai` (existe estilo dele no upstream).

## 14. Riscos e itens não verificados

- **Alias de flavor no Less** (§6): não testei; há plano B.
- **`originalDigest`** (§11): não sei se o Stylus exige.
- **Reimportar por cima:** não sei se o Stylus atualiza ou duplica um estilo de mesmo `@namespace`. Testar e documentar no README (em caso de duplicar, mandar apagar os "… Gibi" antes de reimportar).
- **`overlay0` como texto** (§12): pode ficar fraco em alguns estilos. Se incomodar na prática, clarear só esse slot no `[web]`.
- **Convenção do `mix()`** (§5): confirmar no tooling.
- **Solver de filtros** (§7): a qualidade só se sabe rodando; o limite de perda sai do resultado real.
- **Vazamento de cor** (§10): 58 estilos têm hex literal; o resultado visual só se confirma no navegador.

# Fase 3 — Plasma Style (barras, popups e widgets do Plasma)

> Pré-requisitos: ler `ARCHITECTURE.md` inteiro, `PHASE-2.md` e o `README.md` (seções "Kvantum (fase 2)" e "Limitações conhecidas"). As fases 1 e 2 precisam estar instaladas e funcionando.
>
> Objetivo desta fase: as barras (painéis), os popups do Plasma (lançador, bandeja, calendário, notificações) e os widgets QML do plasmashell ganharem o visual do tema, com o mesmo efeito de **tecla** da fase 2. Hoje eles ainda são desenhados pelo Plasma Style **`MacTahoe-Dark`**, que sobrou do tema anterior e não segue a paleta.
>
> Esta fase tira "Plasma Style" da lista de fora de escopo (`ARCHITECTURE.md` §7). SDDM, splash e cursor continuam fora.

## 0. Antes de começar

1. Confirme que `./install.sh` roda limpo e idempotente (todos os alvos em `sem mudanças`, exceto `kvantum-qt5` como `pulado` se o plugin não foi instalado).
2. Anote o Plasma Style atual: `kreadconfig6 --file plasmarc --group Theme --key name` (nesta máquina: `MacTahoe-Dark`). É o valor que o `uninstall` deve devolver.
3. Leia a documentação oficial de Plasma Style em https://develop.kde.org/docs/plasma/theme/ antes de tocar em SVG. Entenda:
   - a estrutura da pasta (`metadata.json`, `plasmarc`, `colors` opcional, `widgets/`, `dialogs/`, `translucent/`, `solid/`, `opaque/`);
   - a convenção de 9 fatias dos "frame SVGs" (`topleft`, `top`, `topright`, `left`, `center`, `right`, `bottomleft`, `bottom`, `bottomright`), os **prefixos** (`north-`, `south-`, `normal-`, `hover-`, `focus-`…), os elementos `hint-*` (margens, tamanhos) e `shadow-*`/`mask-*`;
   - a **regra de fallback**: arquivo ausente no tema cai no tema `default` (Breeze). Isso permite fazer a fase em ordem de prioridade, sem precisar cobrir tudo.
4. Os IDs reais vêm do tema `default` instalado: `/usr/share/plasma/desktoptheme/default/`. Os arquivos são `.svgz` (gzip). Liste os IDs de cada arquivo com um script antes de desenhar, do mesmo jeito que a fase 2 fez com o KvFlat. Não confie em nome de elemento lembrado de cabeça: confira no arquivo.
5. Trabalhe em commits pequenos, um por etapa da seção 3.

## 1. Base e crédito

Partir do tema **`default` (Breeze)** do Plasma, que está sob LGPL/GPL do próprio Plasma: nomes de arquivos, prefixos, `hint-*` e margens vêm dele; o desenho é refeito pelo gerador. Registrar no `README.md`, abaixo do crédito do KvFlat, o tema base e sua licença (conferir em `/usr/share/licenses/` ou nos cabeçalhos dos SVGs).

## 2. Estrutura do alvo

```
targets/plasma-style/
├── target.toml
├── generate.py                 # como na fase 2: geometria da paleta, cores em ${token}
└── templates/
    └── theme/
        ├── metadata.json       # Id/Name = ${theme_name}, Version com hash do conteúdo
        ├── plasmarc            # blur/contraste
        ├── widgets/*.svg
        ├── dialogs/*.svg
        ├── translucent/...     # variantes usadas com blur (panel, dialogs, tooltip)
        └── solid/...           # variantes opacas (sem composição)
```

- **Reaproveitar o gerador da fase 2.** Mover a parte genérica de `targets/kvantum/generate.py` (`rrect`, `circle`, `clip`, `ring`, `band`, `Paint`/`solid`/`rgba`, fatiamento em 9 peças, saída `<g id>` com retângulo de caixa) para um módulo compartilhado, por exemplo `tooling/svgslice.py`, e fazer os dois geradores importarem dele. O alvo kvantum tem que continuar gerando **exatamente** o mesmo SVG (confirmar com `tests/kvantum-check.py`, que acusa template desatualizado).
- Diferença de convenção: no Kvantum o interior se chama `<elemento>-<estado>` e as bordas `<elemento>-<estado>-<pos>`; no Plasma Style é `<prefixo>-<pos>` com interior `<prefixo>-center` (e sem prefixo para o frame padrão). O fatiador precisa aceitar um esquema de nomes.
- Plasma aceita `.svg` sem compressão. Gerar `.svg` puro (texto), para o render tratar como qualquer template. Conferir que o Plasma 6 de fato carrega `.svg` (e não só `.svgz`) antes de seguir; se não carregar, o alvo comprime no `post` ou o gerador escreve em `build/` já comprimido. Registrar a decisão.
- Destino: `~/.local/share/plasma/desktoptheme/${theme_name}/` (modo `symlink` de diretório, como o alvo kvantum faz com arquivos).
- **Sem arquivo `colors` no tema**: sem ele, o Plasma usa o esquema de cores do sistema (`Gibi.colors`) para texto e ícones, e o tema segue a paleta automaticamente. Só adicionar `colors` se algum contraste falhar.
- **Nenhum hex solto** nos templates (mesmo `grep` da fase 2).
- **Cache:** o Plasma guarda renders de SVG em cache (`~/.cache/`, arquivos `plasma_theme_*` / `ksvg*`; confirmar os nomes nesta versão). O gerador põe um hash do conteúdo em `metadata.json → KPlugin.Version`, o que invalida o cache sozinho quando o tema muda. Se não bastar, um `[[post]]` apaga só os arquivos de cache **deste** tema.

### 2.1 Aplicação e restore

- `[[states]]` com `get = kreadconfig6 --file plasmarc --group Theme --key name`, `set = plasma-apply-desktoptheme "$$GIBI_VALUE"`, `value = ${theme_name}`, `default = "default"`, `reapply_on_change = true` (o conteúdo muda e o nome não).
- Incluir `[plasmarc][Theme] name=${theme_name}` nos `defaults` do pacote Look-and-Feel (alvo `lookandfeel`), para o tema global ficar completo.
- `./uninstall.sh` devolve o Plasma Style anterior (`MacTahoe-Dark` aqui) e remove a pasta do tema.

## 3. Especificação visual, em ordem de prioridade

Regras de sempre (`ARCHITECTURE.md` §3.4): amarelo só pontual, texto sobre amarelo em `accent.on_primary`, roxo como tempero. Nada de janela translúcida: translucidez só em barras e superfícies flutuantes.

### 3.1 Barras (prioridade máxima) — `widgets/panel-background.svg`

- Fundo `base.100` com opacidade `surface.float_opacity` (0.88) nas variantes translúcidas; opaco em `solid/`/`opaque/`. Isso resolve a limitação "Painel" do README (hoje o nível de translucidez vem do MacTahoe).
- Borda interna de 1px `base.70` no lado voltado para a tela (topo da barra de baixo, base da barra de cima). Barra **flutuante**: borda nos 4 lados, cantos `shape.radius_l`, sombra difusa curta (mesmo esquema de camadas das sombras dos menus da fase 2) e `mask-*` para o blur não vazar pela sombra.
- Barra encostada na borda: cantos retos do lado da borda da tela.
- `hint-*` de margens: partir dos valores do Breeze, para os widgets não mudarem de tamanho.
- Conferir no Breeze quais prefixos o Plasma 6 usa para painel flutuante e desenhar esses.

### 3.2 Tarefas — `widgets/tasks.svg`

Os botões do gerenciador de tarefas são o "teclado" da barra:

| Prefixo | Visual |
|---|---|
| `normal` | invisível (só o ícone) |
| `hover` | tecla em hover: face `base.80`, brilho no topo, base inferior, sombra curta |
| `focus` (janela ativa) | tecla em repouso: face `base.90` com base inferior e brilho; sensação de tecla "acesa" |
| `minimized` | plano, sem base, face `base.110` a ~60% |
| `attention` (janela pedindo atenção) | tecla com **base inferior amarela** e borda amarela, como o botão padrão da fase 2; é o único amarelo da barra |

Raio `shape.radius_m`. As peças precisam funcionar tanto em barra horizontal quanto vertical (conferir se o Plasma usa prefixos por orientação).

### 3.3 Popups e dicas — `dialogs/background.svg`, `widgets/tooltip.svg`

- Popups (lançador, bandeja, calendário, notificações, OSD): iguais aos menus do Kvantum: `base.90` a 0.88, borda 1px `base.70`, cantos `shape.radius_l`, sombra em camadas, blur do KWin atrás (`plasmarc` do tema com `[BlurBehindEffect] enabled=true` e contraste neutro).
- Tooltip: `base.140`, borda `base.70`, cantos `shape.radius_s`, opaco.
- `widgets/plasmoidheading.svg` (cabeçalho dos popups): `base.110`, linha de 1px `base.70` embaixo.

### 3.4 Controles QML do Plasma (Plasma Components)

Mesmo desenho dos equivalentes da fase 2, para o Plasma e os apps não parecerem temas diferentes:

1. `widgets/button.svg` e `widgets/actionbutton.svg`: tecla (normal/hover/pressed/focus). O botão de ferramenta (flat) só aparece como tecla no hover.
2. `widgets/lineedit.svg`: campo afundado, anel de foco amarelo de 2px a 45%.
3. `widgets/viewitem.svg`: selecionado em `selection.bg` com borda interna e base sutil; hover `base.70` a 50%.
4. `widgets/checkmarks.svg`, `widgets/radiobutton.svg`, `widgets/switch.svg`: ligado em `accent.secondary` (roxo), marca em `base.10`.
5. `widgets/slider.svg`, `widgets/scrollbar.svg`, `widgets/bar_meter_horizontal.svg` (progresso): trilho `base.120`, preenchimento roxo, alça de tecla em miniatura, pílula fina de rolagem.
6. `widgets/tabbar.svg`: aba ativa com linha amarela de 2px.

O que não estiver nesta lista cai no Breeze. Anotar no README o que ficou com o visual do Breeze.

## 4. Integração

- O alvo `blur` continua ligando o modo translúcido dos painéis; com o Plasma Style próprio, "translúcido" passa a ser exatamente 0.88. Atualizar a linha "Painel" das limitações no README.
- Ordem do alvo: depois de `kvantum` e antes de `lookandfeel` (sugestão: `order = 45`).
- Adicionar ao `install.sh --list`, ao README (tabela de alvos, dependências se houver, créditos) e ao checklist.
- Atualizar `ARCHITECTURE.md` §7: tirar "Plasma Style" de fora de escopo.

## 5. Verificação sem ver a tela

O Claude Code não vê a tela, mas a fase 2 mostrou que dá para conferir quase tudo offscreen. Criar `tests/plasma-style-preview.py` que usa **`QSvgRenderer`** (é o renderizador que o KSvg usa por baixo) para montar, a partir do SVG renderizado em `build/`, uma barra falsa com tarefas nos 5 estados, um popup com cabeçalho, botões, campo, checkbox, switch e slider, e salva em `build/plasma-style-preview.png`. Cada frame é montado com as 9 fatias esticadas, como o Plasma faz. Usar esse preview para iterar antes de aplicar no sistema.

E um `tests/plasma-style-check.py` no mesmo espírito do `kvantum-check.py`: sem hex solto, templates em dia com o gerador, XML válido, e **todo ID que existe no arquivo equivalente do tema `default` e que o tema desenha também existe no nosso** (para não cair no Breeze pela metade dentro de um mesmo arquivo).

## 6. Critérios de aceite

- `./install.sh` idempotente com o novo alvo; `./uninstall.sh` devolve o Plasma Style anterior e remove a pasta do tema; `./uninstall.sh --only plasma-style` idem.
- `tests/selftest.sh`, `tests/kvantum-check.py` (o SVG do Kvantum não mudou com a extração do módulo compartilhado) e `tests/plasma-style-check.py` passam.
- Nenhum hex fora de `palette.toml` nos templates do novo alvo.
- Configurações do Sistema > Aparência > Estilo do Plasma lista **Gibi** sem erro.
- Nenhuma área grande amarela nas barras, popups e notificações (regra 3.4.1).
- `docs/CHECKLIST-FASE-3.md` gerado cobrindo: barra de cima e de baixo (encostada e flutuante), as 5 situações de tarefa (incluindo uma janela pedindo atenção), lançador, bandeja, calendário do relógio, notificação, OSD de volume, tooltip de ícone da barra, e controles dentro de um popup (botão, campo de busca do lançador, switch da bandeja, slider de volume).
- Registrar em `README.md` as limitações encontradas (ex.: widgets que o Plasma desenha fora do Plasma Style, plasmoides de terceiros com cores próprias).

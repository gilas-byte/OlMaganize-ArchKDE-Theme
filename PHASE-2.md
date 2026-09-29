# Fase 2 — Kvantum com efeito de tecla

> Pré-requisitos: ler `ARCHITECTURE.md` inteiro e `docs/PHASE-2-NOTES.md` (gerado na fase 1). A fase 1 precisa estar instalada e funcionando.
>
> Objetivo desta fase: os widgets dos apps Qt/KDE ganharem o visual de **tecla/botão de videogame** descrito em `ARCHITECTURE.md` §3.5, substituindo o Klassy como estilo de widgets. O Klassy **continua** como decoração de janela.

## 0. Antes de começar

1. Confirme que `./install.sh` da fase 1 roda limpo e idempotente.
2. Pacotes: `kvantum` (Qt6) e, se houver apps Qt5 no sistema, `kvantum-qt5`. Verificar disponibilidade conforme a fase 1.
3. Leia a documentação de criação de temas do Kvantum (o "Theme-Making" do repositório do Kvantum) antes de tocar em SVG. Entenda a convenção de IDs dos elementos (`<elemento>-normal`, `-focused`, `-pressed`, `-toggled`, `-disabled`, e os sufixos de bordas/cantos `-top`, `-bottom`, `-left`, `-topleft` etc.).

## 1. Escolha do tema base

Não desenhar do zero. Partir de um tema existente e **retemplatizar**.

Critérios:
1. Licença compatível com GPL-3.0. Preferência: um dos temas que vêm junto com o próprio Kvantum (`/usr/share/Kvantum/`), que já estão sob a licença do Kvantum.
2. Visual plano e simples, com botões de forma retangular arredondada (fácil de adicionar o efeito de tecla).
3. Funciona bem em Qt6.

Registrar no `README.md` qual tema foi usado como base e sua licença, abaixo dos créditos à Cecilia May.

## 2. Estrutura do alvo

```
targets/kvantum/
├── target.toml
└── templates/
    └── Gibi/
        ├── Gibi.kvconfig    # com ${tokens}
        └── Gibi.svg         # com ${tokens}
```

- Destino: `~/.config/Kvantum/Gibi/` (modo `symlink`).
- `~/.config/Kvantum/kvantum.kvconfig` → `theme=Gibi` via `managed-block` ou chave única, com backup.
- **Nenhum hex solto** no SVG ou no kvconfig: toda cor é placeholder de `palette.toml`. Opacidades podem ser literais nos atributos `fill-opacity`/`stroke-opacity`, mas prefira tokens quando representarem um token de `ARCHITECTURE.md` (ex.: `keycap.base_color`).

## 3. Especificação visual

### 3.1 Botões (prioridade máxima)

Implementar os estados de `ARCHITECTURE.md` §3.5 nos elementos de botão (`button`) e botão de ferramenta (`tbutton`):

| Estado | Fundo | Detalhes |
|---|---|---|
| normal | `base.90` | brilho 1px no topo (`keycap.highlight`), borda interna 1px (`shape.border_color`), base inferior de `keycap.base_depth` px (`keycap.base_color`), drop curto |
| focused (hover no Kvantum) | `base.80` | mesmos detalhes |
| pressed | `base.110` | **sem** base inferior e **sem** drop; conteúdo 1px abaixo (usar o deslocamento de texto do kvconfig, se disponível) |
| toggled | `selection.bg` | como pressed, texto `selection.fg` |
| disabled | `base.120` | sem sombras; opacidade de texto conforme kvconfig |

Botão padrão / principal (default button): fundo `accent.primary`, texto `accent.on_primary`, mesmos detalhes de tecla. É **o único** lugar onde o amarelo vira preenchimento.

Anel de foco de teclado: 2px `accent.primary` a ~45% (elemento de foco do Kvantum).

Raio: `shape.radius_m`.

### 3.2 Demais widgets, em ordem

1. **Itens de lista / árvore selecionados**: fundo `selection.bg` com borda interna + base inferior sutil (como o item selecionado na sidebar do Obsidian Primary). Hover: `base.80`.
2. **Campos de texto e combos**: fundo `base.120`, borda interna 1px, **sem** base inferior (campo é "afundado", não tecla); foco com o anel amarelo.
3. **Checkbox e radio**: desligado = `base.120` com borda; ligado = `accent.secondary` com marca em `base.10`. (Roxo aqui, não amarelo, para não espalhar amarelo.)
4. **Abas**: aba ativa = `base.100` com linha inferior de 2px `accent.primary`; inativas = `base.110`, texto `base.40`.
5. **Scrollbars**: trilho invisível ou `base.110`; alça `base.70`, hover `base.60`; finas; sem efeito de tecla.
6. **Sliders e progress**: trilho `base.120`; preenchimento `accent.secondary` (roxo); alça do slider com efeito de tecla em miniatura.
7. **Menus e popups**: fundo `base.90` com `surface.float_opacity` e blur leve (opções `translucent_windows=false`, blur/translucidez **só** para popups/menus no kvconfig). Item em hover = `selection.bg_subtle`.
8. **Tooltips**: `base.140`, texto `base.20`, borda `base.70`.

Janelas continuam **opacas**.

## 4. Integração

- Trocar o `widgetStyle` na fonte única criada na fase 1 de `Klassy` para `kvantum`. Isso deve propagar para o `kdeglobals` e para o pacote Look-and-Feel sem editar mais nada.
- Rever o alvo `blur` da fase 1: se os menus ficaram opacos lá por falta de opção no Klassy, agora a translucidez/blur de popups vem do kvconfig. Não duplicar a configuração.
- `uninstall.sh` precisa devolver `widgetStyle` ao valor anterior (Klassy, se a fase 1 estava instalada).
- Adicionar ao `install.sh --list` e ao checklist.

## 5. Critérios de aceite

- `./install.sh` idempotente com o novo alvo; `./uninstall.sh` volta limpo.
- Nenhum hex fora de `palette.toml` (fazer um `grep` de `#[0-9A-Fa-f]{6}` em `targets/kvantum/templates/` e confirmar zero ocorrências).
- Kvantum Manager (`kvantummanager`) reconhece o tema sem erros.
- Nenhuma área grande amarela em Dolphin, Configurações do Sistema, Kate e diálogos de arquivo (regra 3.4.1).
- `docs/CHECKLIST-FASE-2.md` gerado cobrindo: botões nos 5 estados (incluindo botão padrão amarelo em um diálogo de confirmação), foco por teclado (Tab), listas selecionadas, campos, checkbox/radio, abas, scrollbar, slider, menus com blur, tooltips, e um app Qt5 se existir no sistema.
- Registrar em `README.md` as limitações encontradas (ex.: widgets que o Kvantum não consegue desenhar como especificado).

# Filtros CSS do alvo stylus

A lib dos userstyles do Catppuccin tem um segundo mapa, `@catppuccin-filters`, com uma cadeia
`brightness(0) saturate(100%) invert() sepia() saturate() hue-rotate() brightness() contrast()`
por cor. Os estilos usam isso para recolorir ícones e SVGs pretos (`filter: @blue-filter`).

`targets/stylus/cssfilter.py` recalcula essas cadeias para a paleta do Gibi com o mesmo solver
SPSA do "CSS filter generator" (o que gerou os filtros originais). É determinístico: seed = cor +
número da tentativa, 20 tentativas por cor, iterações fixas. Os resultados ficam em
`targets/stylus/filters.json` (commitado) e só são recalculados quando uma cor muda ou quando
`cssfilter.VERSION` muda (~0,6 s por cor).

## Perda

A perda é a do gerador original: soma das diferenças absolutas em R, G, B (0-255) e em H, S, L
(0-100), medida já com os valores arredondados que vão para o CSS. Referência do gerador:
abaixo de 1 é exato, abaixo de 5 é "perto o bastante".

**Limite: 5** (`cssfilter.LOSS_LIMIT`). Uma cor acima disso faz o `generate.py` falhar e o alvo
dá erro no install. Com a paleta atual a pior perda é 2,17 (`red`), com erro máximo de 1/255 por
canal, então sobra folga para mudar a paleta sem ajustar o solver.

| slot | token | cor | perda | erro máx. por canal |
|---|---|---|---|---|
| rosewater | `web.rosewater` | #E6A8AB | 0.71 | 0 |
| flamingo | `web.flamingo` | #E38D9C | 0.61 | 0 |
| pink | `sem.pink` | #E06C8A | 0.50 | 0 |
| mauve | `accent.secondary` | #F9CF51 | 2.09 | 1 |
| red | `sem.red` | #E4574E | 2.17 | 1 |
| maroon | `web.maroon` | #E35E63 | 0.57 | 0 |
| peach | `sem.orange` | #EEA359 | 2.09 | 1 |
| yellow | `sem.yellow` | #F9CF51 | 2.09 | 1 |
| green | `sem.green` | #64C271 | 0.60 | 0 |
| teal | `web.teal` | #60B894 | 0.98 | 0 |
| sky | `web.sky` | #7FBABB | 1.02 | 1 |
| sapphire | `web.sapphire` | #5FA6BC | 0.82 | 0 |
| blue | `sem.blue` | #639CC0 | 0.59 | 0 |
| lavender | `base.40` | #AB916D | 0.72 | 0 |
| text | `base.10` | #EBDAC6 | 1.37 | 0 |
| subtext1 | `base.20` | #D7C0A3 | 1.79 | 1 |
| subtext0 | `web.subtext0` | #C1A888 | 0.57 | 0 |
| overlay2 | `base.40` | #AB916D | 0.72 | 0 |
| overlay1 | `base.50` | #917959 | 1.41 | 1 |
| overlay0 | `base.60` | #6B563D | 1.57 | 1 |
| surface2 | `base.70` | #51402F | 0.21 | 0 |
| surface1 | `base.80` | #3B3026 | 1.04 | 0 |
| surface0 | `base.90` | #342C23 | 0.47 | 0 |
| base | `base.100` | #2E261F | 0.47 | 0 |
| mantle | `base.120` | #26211C | 0.61 | 0 |
| crust | `base.140` | #1C1712 | 0.65 | 0 |
| primary | `accent.primary` | #FFEA00 | 0.15 | 0 |

O "erro máx. por canal" é o resultado da cadeia simulada com as matrizes da spec de Filter
Effects, arredondado. O navegador usa as mesmas matrizes, mas a confirmação visual (ícones
recoloridos) fica no `docs/CHECKLIST-FASE-4.md`.

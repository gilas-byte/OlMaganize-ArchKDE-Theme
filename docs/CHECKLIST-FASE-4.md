# Checklist visual — Fase 4 (Stylus: páginas web)

O Claude Code não vê o navegador. Tudo o que dá para testar sem ele já é coberto por `tests/stylus-check.py`: lib, filtros, header, `import.json`, contraste, e os 134 estilos compilando com less.js. O que sobra está aqui. Para cada item, tire um screenshot da janela do Brave:

```sh
spectacle -b -a -n -d 3000 -o ~/gibi-check-web-<site>.png
```

Regra de ouro (ARCHITECTURE.md §3.4): **nenhuma área grande amarela** e **nenhum roxo/lilás**. Nas páginas o fundo é marrom (`base.100`), o texto é bege e o accent é o amarelo suave (`#F9CF51`).

## Antes de tudo

- [ ] `./install.sh --only stylus` sem erro. A mensagem mostra o caminho do `import.json`. Rodando de novo: `sem mudanças`.
- [ ] `python3 tests/stylus-check.py` termina com `Stylus OK.`

## Importação (itens não verificados do PHASE-4 §14)

- [ ] No Stylus (ícone → **Gerenciar**), **apague ou desative** todos os "… Catppuccin".
- [ ] **Importar** → `~/.local/share/gibi/stylus/import.json`. Sem erro, e aparecem **134 estilos "… Gibi"**, todos ligados. O arquivo leva `originalDigest` (sha1 do código, igual ao import do Catppuccin). Se a importação falhar ou nada aparecer, **anote a mensagem**: é o primeiro suspeito.
- [ ] Abra um estilo (ex.: "GitHub Gibi") → ícone de engrenagem/opções: **Light Flavor** e **Dark Flavor** só têm "Gibi"; **Accent** tem Amarelo (padrão), Amarelo vivo, Pêssego… Cinza, **sem Mauve nem Lavender**.
- [ ] No editor do estilo, sem aviso de erro de compilação (barra vermelha no topo).
- [ ] **Sem atualização automática:** Gerenciar → "Verificar atualizações" não oferece trocar nenhum "… Gibi" pelo original.
- [ ] **Reimportar por cima:** importe o mesmo arquivo de novo. O Stylus **atualizou** os estilos (continuam 134) ou **duplicou** (268)? Anote. Se duplicou, apague os duplicados; o README já manda apagar os "… Gibi" antes de reimportar, e eu tiro a ressalva se ele atualizar.

## Sites — um screenshot por site

Em cada um: fundo marrom, texto bege legível, links/destaques em amarelo suave, **nada lilás ou azul-pastel sobrando**.

- [ ] **GitHub** (`github.com/<qualquer repo>`): página do repo, um arquivo de código e um diff de PR. Código legível; adições e remoções em verde e vermelho sobre marrom. O GitHub é o 2º estilo com mais cor escrita à mão (82 hex, 38 coloridos): anote o que ficar pastel/azulado.
- [ ] **YouTube**: home, um vídeo e a barra de progresso. Ícones da barra lateral recoloridos (filtros).
- [ ] **Arch Wiki** (`wiki.archlinux.org`): texto, blocos de código, caixas de nota/aviso. Logo recolorido (filtro).
- [ ] **Wikipedia**: artigo com infobox e uma tabela. É o estilo com mais filtros (14): ícones da barra de ferramentas recoloridos, nenhum preto sobre marrom.
- [ ] **Google**: página de resultados. Tem 12 hex fixos (quase todos em seletores): anote se o logo ou algum botão ficou fora do tom.
- [ ] **Stack Overflow**: uma pergunta com bloco de código (realce vindo do CSS externo, que lê `--ctp-*`): cores do código dentro da paleta.
- [ ] **claude.ai**: conversa com bloco de código e o campo de mensagem.

## Detalhes

- [ ] **Ícones recoloridos (filtros):** em pelo menos um dos sites acima, um ícone monocromático aparece bege ou amarelo, não preto nem com cor estranha. A cor simulada erra no máximo 1/255 por canal (`docs/STYLUS-FILTERS.md`); aqui é a confirmação no navegador real.
- [ ] **Accent vivo:** num estilo, troque Accent → **Amarelo vivo**. O accent vira `#FFEA00`. Veja se algum elemento grande fica amarelo (regra 3.4.1). Se ficar, anote o site e volte para Amarelo.
- [ ] **Tema claro do sistema/site:** num site com seletor de tema (GitHub: Settings → Appearance → Light), a página continua marrom (o flavor claro também é o Gibi).
- [ ] **`overlay0` como texto** (2.14:1, fraco de propósito): se você usa algum destes, veja se o texto apagado ainda dá para ler: twitter/X, npm, anilist, vikunja, migadu, picrew, advent-of-code (lista completa no `build/stylus-report.md`).
- [ ] **Vazamento de cor:** nos sites que você usa de verdade, anote qualquer pedaço pastel (azul, lilás, rosa claro) que destoe. `build/stylus-report.md` diz se o estilo tem hex fixo e em que linha: é a lista de trabalho da fase 4.1.

## Desinstalação

- [ ] `./uninstall.sh --only stylus` remove `~/.local/share/gibi/stylus/`. Os estilos importados continuam no Stylus (o alvo não mexe no navegador): apague os "… Gibi" à mão e reative os "… Catppuccin" se quiser voltar.

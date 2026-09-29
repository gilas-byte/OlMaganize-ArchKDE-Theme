# Gibi

> **Créditos:** a paleta e a sensação visual deste tema vêm do **[Primary for Obsidian](https://github.com/primary-theme/obsidian)**, de **Cecilia May**. Ele serviu de inspiração e é a fonte da paleta base. Nenhum código do Primary foi copiado, só os valores de cor.

Tema retro-moderno para **Arch Linux / CachyOS com KDE Plasma 6**: marrons quentes, texto bege, sensação de revista antiga e um acento amarelo vivo. "Gibi" é um codinome provisório. O nome fica em um único lugar (`palette.toml → [theme]`).

## Instalação

```sh
./install.sh                 # render + checagem de contraste + aplica todos os alvos detectados
./install.sh --only ghostty  # só um alvo (ou vários: --only gtk,ghostty)
./install.sh --dry-run       # mostra o que faria, sem alterar nada
./install.sh --list          # lista os alvos e se foram detectados
./uninstall.sh               # restaura os backups (arquivos e chaves do KDE)
```

Tudo vai para `~`. `sudo` só aparece no `pacman -S` de dependências que faltam, e sempre com confirmação. Antes de mexer em qualquer coisa, o instalador guarda um backup em `~/.local/state/gibi/backups/<timestamp>/` com um `manifest.json`.

## Licença

GPL-3.0. Ver `LICENSE`.

#!/usr/bin/env bash
# Amostra da paleta ANSI 0-15 e de estilos comuns, para conferir o tema do terminal.
names=(black red green yellow blue magenta cyan white)

printf '\n  normal   '
for i in {0..7}; do printf '\e[48;5;%dm  %-7s\e[0m' "$i" "${names[i]}"; done
printf '\n  bright   '
for i in {8..15}; do printf '\e[48;5;%dm  %-7s\e[0m' "$i" "${names[i-8]}"; done
printf '\n\n  texto    '
for i in {0..7}; do printf '\e[38;5;%dm%-9s\e[0m' "$i" "${names[i]}"; done
printf '\n  bright   '
for i in {8..15}; do printf '\e[38;5;%dm%-9s\e[0m' "$i" "${names[i-8]}"; done
printf '\n\n  \e[1mnegrito\e[0m  \e[2mapagado\e[0m  \e[3mitálico\e[0m  \e[4msublinhado\e[0m  \e[7minvertido\e[0m\n'
printf '  \e[31merro\e[0m  \e[33maviso\e[0m  \e[32msucesso\e[0m  \e[34minfo\e[0m  \e[35mreferência\e[0m\n'
printf '  ícones nerd font: \uf015 \ue725 \uf07b \uf121 \ue0b0\n\n'

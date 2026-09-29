#!/usr/bin/env bash
# Uso: apply.sh <tema>
# O plasma-apply-desktoptheme recusa reaplicar o tema ativo. Quando o conteúdo do tema muda
# sem o nome mudar, passa um instante pelo Breeze para o plasmashell recarregar os SVGs.
set -euo pipefail
current=$(kreadconfig6 --file plasmarc --group Theme --key name)
if [[ "$current" == "$1" ]]; then
    plasma-apply-desktoptheme default >/dev/null
fi
exec plasma-apply-desktoptheme "$1"

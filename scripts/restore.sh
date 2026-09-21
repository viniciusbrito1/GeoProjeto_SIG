#!/usr/bin/env bash
# RNF-06: restauração a partir de um backup gerado por scripts/backup.sh.
# ATENÇÃO: substitui os dados atuais do banco (--clean --if-exists).
set -euo pipefail
cd "$(dirname "$0")/.."

if [ $# -ne 1 ]; then
    echo "Uso: $0 <arquivo_de_backup.dump>" >&2
    exit 1
fi
ARQUIVO="$1"

set -a
source .env
set +a

docker compose exec -T postgis pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists < "$ARQUIVO"
echo "Restauração concluída a partir de $ARQUIVO."

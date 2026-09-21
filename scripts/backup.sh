#!/usr/bin/env bash
# RNF-06: rotina de backup. Roda dentro do container `postgis` via
# `docker compose exec`, então não precisa de cliente Postgres na máquina host.
set -euo pipefail
cd "$(dirname "$0")/.."

set -a
source .env
set +a

DESTINO="${1:-backup_$(date +%Y%m%d_%H%M%S).dump}"

docker compose exec -T postgis pg_dump -U "$POSTGRES_USER" -Fc "$POSTGRES_DB" > "$DESTINO"
echo "Backup salvo em $DESTINO ($(du -h "$DESTINO" | cut -f1))."

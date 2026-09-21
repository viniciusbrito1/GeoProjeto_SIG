#!/usr/bin/env bash
# RNF-06 pede uma rotina de backup "com restauração comprovadamente testada"
# — não basta o script rodar sem erro, tem que provar que os dados voltam
# íntegros. Este script faz o ciclo completo contra um banco descartável
# (nunca toca no banco em uso) e compara contagem de linhas antes/depois.
set -euo pipefail
cd "$(dirname "$0")/.."

set -a
source .env
set +a

DB_TESTE="siscoord_teste_restore_$$"
DUMP_TMP="$(mktemp)"
trap 'rm -f "$DUMP_TMP"; docker compose exec -T postgis psql -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_TESTE" > /dev/null' EXIT

echo "1/4 — gerando backup do banco atual ($POSTGRES_DB)..."
docker compose exec -T postgis pg_dump -U "$POSTGRES_USER" -Fc "$POSTGRES_DB" > "$DUMP_TMP"

echo "2/4 — criando banco descartável ($DB_TESTE) e restaurando o dump nele..."
docker compose exec -T postgis psql -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE $DB_TESTE"
docker compose exec -T postgis pg_restore -U "$POSTGRES_USER" -d "$DB_TESTE" < "$DUMP_TMP"

echo "3/4 — comparando contagem de linhas..."
FALHOU=0
for TABELA in usuarios orgaos recursos ocorrencias demandas empenhos auditoria; do
    ORIGINAL=$(docker compose exec -T postgis psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT count(*) FROM $TABELA")
    RESTAURADO=$(docker compose exec -T postgis psql -U "$POSTGRES_USER" -d "$DB_TESTE" -tAc "SELECT count(*) FROM $TABELA")
    if [ "$ORIGINAL" != "$RESTAURADO" ]; then
        echo "  ✗ $TABELA: original=$ORIGINAL restaurado=$RESTAURADO"
        FALHOU=1
    else
        echo "  ✓ $TABELA: $ORIGINAL linhas nos dois bancos"
    fi
done

echo "4/4 — limpando banco descartável (feito automaticamente ao sair)."

if [ "$FALHOU" -eq 0 ]; then
    echo "Backup/restauração validado: todas as tabelas batem."
else
    echo "FALHA: alguma tabela não bateu — não confie neste backup." >&2
    exit 1
fi

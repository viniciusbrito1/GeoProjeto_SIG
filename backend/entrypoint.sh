#!/usr/bin/env bash
set -e

echo "Aguardando banco de dados..."
python - <<'PY'
import time
import psycopg
from app.config import get_settings

url = get_settings().database_url_migracao.replace("postgresql+psycopg://", "postgresql://")
for _ in range(60):
    try:
        with psycopg.connect(url, connect_timeout=2):
            break
    except Exception:
        time.sleep(2)
else:
    raise SystemExit("Banco de dados não respondeu a tempo.")
PY

echo "Aplicando migrações..."
alembic upgrade head

echo "Carregando dados de referência..."
python - <<'PY'
from pathlib import Path
import psycopg
from app.config import get_settings

url = get_settings().database_url_migracao.replace("postgresql+psycopg://", "postgresql://")
sql = Path("sql/seed_referencia.sql").read_text(encoding="utf-8")
with psycopg.connect(url) as conn:
    conn.execute(sql)
    conn.commit()
PY

echo "Garantindo usuário Coordenador inicial..."
python -m app.seed.bootstrap_admin

echo "Iniciando API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

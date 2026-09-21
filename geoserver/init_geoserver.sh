#!/bin/sh
# Publica as camadas operacionais como WMS 1.3.0 / WFS 2.0.0 (RF-11), direto
# do mesmo banco PostGIS que a API usa (RNF-01: um SGBD só, nada de camada
# espacial duplicada). Roda uma vez, como serviço one-shot do docker-compose,
# depois que o GeoServer sobe — é idempotente, então reexecutar não quebra
# nada (os POSTs que já existem apenas retornam um erro que o `|| true` engole).
set -e

GS_URL="${GEOSERVER_URL:-http://geoserver:8080/geoserver}"
GS_USER="${GEOSERVER_ADMIN_USER:-admin}"
GS_PASS="${GEOSERVER_ADMIN_PASSWORD:-geoserver}"
WORKSPACE="siscoord"
DB_HOST="${DB_HOST:-postgis}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-siscoord}"
DB_USER="siscoord_app"
DB_PASS="${APP_DB_PASSWORD:?defina APP_DB_PASSWORD no .env}"

echo "Aguardando GeoServer ficar pronto..."
until curl -sf -u "$GS_USER:$GS_PASS" "$GS_URL/rest/about/version.json" > /dev/null 2>&1; do
  sleep 3
done

echo "Criando workspace '$WORKSPACE'..."
curl -s -u "$GS_USER:$GS_PASS" -X POST -H "Content-Type: application/json" \
  -d "{\"workspace\":{\"name\":\"$WORKSPACE\"}}" \
  "$GS_URL/rest/workspaces" || true

echo "Criando datastore PostGIS 'siscoord_db'..."
curl -s -u "$GS_USER:$GS_PASS" -X POST -H "Content-Type: application/json" \
  -d "{
    \"dataStore\": {
      \"name\": \"siscoord_db\",
      \"connectionParameters\": {
        \"entry\": [
          {\"@key\": \"host\", \"\$\": \"$DB_HOST\"},
          {\"@key\": \"port\", \"\$\": \"$DB_PORT\"},
          {\"@key\": \"database\", \"\$\": \"$DB_NAME\"},
          {\"@key\": \"user\", \"\$\": \"$DB_USER\"},
          {\"@key\": \"passwd\", \"\$\": \"$DB_PASS\"},
          {\"@key\": \"dbtype\", \"\$\": \"postgis\"},
          {\"@key\": \"schema\", \"\$\": \"public\"},
          {\"@key\": \"Expose primary keys\", \"\$\": \"true\"}
        ]
      }
    }
  }" \
  "$GS_URL/rest/workspaces/$WORKSPACE/datastores" || true

publicar_camada() {
  camada="$1"
  echo "Publicando camada '$camada'..."
  curl -s -u "$GS_USER:$GS_PASS" -X POST -H "Content-Type: application/json" \
    -d "{\"featureType\":{\"name\":\"$camada\",\"srs\":\"EPSG:4674\",\"nativeCRS\":\"EPSG:4674\",\"title\":\"$camada\"}}" \
    "$GS_URL/rest/workspaces/$WORKSPACE/datastores/siscoord_db/featuretypes" || true
}

publicar_camada "recursos"
publicar_camada "ocorrencias"

echo "GeoServer configurado. WMS: $GS_URL/$WORKSPACE/wms · WFS: $GS_URL/$WORKSPACE/wfs"

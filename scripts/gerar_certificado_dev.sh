#!/usr/bin/env bash
# Gera um certificado autoassinado para desenvolvimento/homologação (RNF-06:
# HTTPS obrigatório). Em produção, troque nginx/certs/siscoord.{crt,key} por
# um certificado emitido de verdade (Let's Encrypt/certbot, ICP interna do
# órgão, etc.) — o navegador vai acusar "não confiável" com autoassinado.
set -e

DESTINO="$(dirname "$0")/../nginx/certs"
mkdir -p "$DESTINO"

if [ -f "$DESTINO/siscoord.crt" ]; then
    echo "Certificado já existe em $DESTINO — nada a fazer. Apague-o antes para gerar outro."
    exit 0
fi

# MSYS_NO_PATHCONV evita que o Git Bash do Windows "corrija" o -subj (que
# começa com /) como se fosse um caminho de arquivo — inofensivo em Linux/macOS.
MSYS_NO_PATHCONV=1 openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$DESTINO/siscoord.key" \
    -out "$DESTINO/siscoord.crt" \
    -subj "/C=BR/O=Defesa Civil Estadual/OU=SISCOORD-DC/CN=localhost"

echo "Certificado autoassinado gerado em $DESTINO."

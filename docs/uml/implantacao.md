# Diagrama de implantação

Topologia dos containers Docker Compose ([`docker-compose.yml`](../../docker-compose.yml))
numa única máquina (o RNF-07 pede implantação em uma máquina limpa em até 60
minutos — não há dependência de infraestrutura distribuída).

```mermaid
flowchart TB
    subgraph Host["Host Docker (1 máquina)"]
        subgraph Net["rede interna docker-compose"]
            Proxy["📦 proxy<br/>nginx:1.27-alpine<br/>portas host: 80, 443"]
            FE["📦 frontend<br/>nginx + build estático React"]
            BE["📦 backend<br/>FastAPI (uvicorn)<br/>porta host: 127.0.0.1:8000"]
            GS["📦 geoserver<br/>kartoza/geoserver:2.25<br/>porta host: 127.0.0.1:8080"]
            GSInit["📦 geoserver-init<br/>one-shot: publica camadas<br/>(RF-11), depois encerra"]
            PG[("📦 postgis<br/>postgis/postgis:16-3.4<br/>volume: postgis_data")]
        end
        Certs[("nginx/certs/<br/>certificado TLS")]
    end

    Internet(("Rede do órgão /<br/>Internet")) -- "443 (HTTPS)" --> Proxy
    Proxy --> FE
    Proxy --> BE
    Proxy -->|"/geoserver/* após<br/>verificar login na API"| GS
    BE --> PG
    GS --> PG
    GSInit -.->|"configura na subida,<br/>depois some"| GS
    GSInit -.-> PG
    Proxy -.-> Certs

    ExtWMS(("Provedor WMS<br/>externo (RF-15)")) -. "consumido direto<br/>pelo navegador" .-> Internet
```

## Requisitos de máquina

| Item | Mínimo recomendado |
|---|---|
| CPU | 2 vCPU |
| RAM | 4 GB (GeoServer sozinho pede ~1 GB) |
| Disco | 10 GB livres (volumes crescem com o histórico de auditoria e os dados espaciais) |
| Software | Docker Engine + Docker Compose plugin |
| Rede | portas 80 e 443 livres; 8000 e 8080 livres no loopback (`127.0.0.1`) — usadas só para diagnóstico e administração local, nunca expostas à rede (RNF-06) |

## Por que um `geoserver-init` que "aparece e some"

GeoServer não vem com workspace/datastore/camadas pré-configurados — isso
normalmente é um passo manual no console web. `geoserver-init`
([`geoserver/init_geoserver.sh`](../../geoserver/init_geoserver.sh)) é um
container *one-shot*: sobe depois que `geoserver` e `backend` estão
saudáveis, chama a REST API do GeoServer para criar o workspace `siscoord`,
o datastore PostGIS e publicar as camadas `recursos`/`ocorrencias`, e
termina. É reexecutável sem efeito colateral (idempotente) — rodar
`docker compose up` de novo não duplica nada.

## Passo a passo de implantação

Ver [manual-instalacao.md](../manual-instalacao.md) para o procedimento
completo, escrito para alguém que nunca viu o projeto (RNF-07).

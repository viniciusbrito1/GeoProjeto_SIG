# SISCOORD-DC

**Sistema de Coordenação Geoespacial de Recursos de Defesa Civil.**

Repositório: <https://github.com/viniciusbrito1/GeoProjeto_SIG>

Coordena equipes, instalações e equipamentos de defesa civil entre municípios
atingidos por chuvas acima da média: cadastro georreferenciado de recursos,
registro de ocorrências e demandas, empenho/liberação com trilha de auditoria,
mapa interativo com camadas OGC (WMS/WFS) e geração de relatórios de situação
(SITREP).

Implementado a partir do [Documento de Requisitos v2.0](docs/requisitos/Lista_Requisitos_SISCOORD-DC.pdf)
(25 requisitos — 15 funcionais, 10 não funcionais). A [matriz de
rastreabilidade](docs/matriz-rastreabilidade.md) mostra onde cada um está implementado e como testá-lo.

## Stack

| Camada | Tecnologia | Por quê |
|---|---|---|
| Banco de dados | PostgreSQL 16 + PostGIS 3.4 | geometria e atributos no mesmo SGBD, índice espacial GiST (RNF-01) |
| Camadas OGC | GeoServer | publica WMS 1.3.0 / WFS 2.0.0 padrão a partir do PostGIS, sem reinventar servidor de mapas (RF-11) |
| API | FastAPI (Python) + SQLAlchemy/GeoAlchemy2 | regras de negócio, RBAC, auditoria, relatórios |
| Frontend | React + TypeScript + Leaflet | mapa interativo, desenho de área, consumo de WMS/WFS |
| Orquestração | Docker Compose + nginx (TLS) | subir tudo com um comando (RNF-07) |

Todos os componentes são software livre (RNF-09) — ver [LICENSE](LICENSE).

## Arquitetura

Ver [docs/arquitetura.md](docs/arquitetura.md) para a visão completa. Resumo:
API e GeoServer leem o **mesmo** banco PostGIS — não existe um "banco de
negócio" separado de um "banco espacial" (RNF-01 veda arquitetura dual). A
trilha de auditoria (RF-13) é gravada por *trigger* de banco, com o papel de
conexão da API sem permissão de escrita nela — não editável pela aplicação
por construção, não por convenção.

## Subir o sistema

Pré-requisitos: Docker e Docker Compose. Passo a passo completo, incluindo
geração de certificado HTTPS e verificação de que tudo subiu: [docs/manual-instalacao.md](docs/manual-instalacao.md).

```bash
git clone https://github.com/viniciusbrito1/GeoProjeto_SIG.git
cd GeoProjeto_SIG
cp .env.example .env
# edite o .env e troque todas as senhas/segredos antes de continuar
bash scripts/gerar_certificado_dev.sh
docker compose up -d --build
```

Acesse `https://localhost` (certificado autoassinado — o navegador vai
avisar; isso é esperado em desenvolvimento, ver o manual de instalação para
produção). Um usuário Coordenador é criado automaticamente a partir de
`ADMIN_EMAIL`/`ADMIN_SENHA` do `.env`.

- Frontend: `https://localhost`
- API + documentação interativa (Swagger): `https://localhost/api/docs`
- Camadas OGC (WMS/WFS): `https://localhost/geoserver/siscoord/wms` e `.../wfs` — exigem login
  (no navegador, a sessão do sistema; em QGIS e afins, e-mail e senha de um usuário ativo via HTTP Basic)
- GeoServer (console de administração): `http://localhost:8080/geoserver` — só a partir da própria máquina do servidor (porta configurável em `GEOSERVER_PORTA_HOST` no `.env`)

Por segurança (RNF-06), as portas 8000 (API) e 8080 (GeoServer) só aceitam
conexões do próprio host; pela rede, tudo passa pelo HTTPS do `proxy`.

## Dados de exemplo (teste de escala — RNF-10)

```bash
docker compose exec backend python -m app.seed.seed_escala --recursos 600 --ocorrencias 25
```

Gera >=500 recursos e >=20 ocorrências (com alguns empenhos ativos) para
testar a carga de 20 usuários simultâneos exigida pelo RNF-10.

## Testes

```bash
docker compose exec backend pytest -v
```

A suíte tem 36 testes (todos passando na última execução, em 21/09/2026). Eles rodam contra o banco real dentro de transações com `SAVEPOINT`
(rollback automático por teste) — por isso exercitam de verdade os
triggers e constraints do Postgres (ex.: o índice único que impede duplo
empenho, OBJ-3), não apenas a camada de serviço em Python.

## Documentação

- [Arquitetura](docs/arquitetura.md)
- [Modelo de dados](docs/modelo-dados.md)
- [Manual de instalação](docs/manual-instalacao.md)
- [Matriz de rastreabilidade](docs/matriz-rastreabilidade.md) (RF/RNF → componente → teste)
- [Conformidade (LGPD / IDE-Defesa / software livre)](docs/conformidade.md)
- Diagramas UML: [casos de uso](docs/uml/casos-de-uso.md) · [classes](docs/uml/classes.md) · [sequência (empenho)](docs/uml/sequencia-empenho.md) · [implantação](docs/uml/implantacao.md)
- **Versão em PDF de toda a documentação**, diagramas em PNG e apresentação: [`docs/entrega/`](docs/entrega/) (índice em [`LEIA-ME.txt`](docs/entrega/LEIA-ME.txt))
- Requisitos de origem: [Lista de Requisitos v2.0](docs/requisitos/Lista_Requisitos_SISCOORD-DC.pdf)
- **Gestão do projeto** ([índice](docs/gestao/README.md)): [termo de abertura](docs/gestao/termo-abertura.md) · [EAP e dicionário](docs/gestao/eap.md) · [cronograma e caminho crítico](docs/gestao/cronograma.md) · [RACI](docs/gestao/organizacao-raci.md) · [partes interessadas e comunicação](docs/gestao/partes-interessadas.md) · [riscos](docs/gestao/riscos.md) · [controle de mudanças](docs/gestao/controle-mudancas.md) · [relatório de situação](docs/gestao/status-projeto.md)

## Estrutura do repositório

```
backend/    API FastAPI, modelos, migrações Alembic, testes
frontend/   React + Leaflet
geoserver/  script de publicação das camadas WMS/WFS
nginx/      proxy reverso com TLS
docs/       documentação técnica, UML, gestão (docs/gestao/), PDFs e diagramas (docs/entrega/)
scripts/    utilitários (certificado dev, backup/restore)
```

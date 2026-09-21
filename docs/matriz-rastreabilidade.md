# Matriz de rastreabilidade

Cada requisito do Documento de Requisitos v2.0 (25 no total — 15 funcionais,
10 não funcionais), o(s) componente(s) que o implementam, e como verificar
que está atendido. "Verificação" é um teste automatizado quando é possível
automatizar; senão, um procedimento manual objetivo.

## Requisitos funcionais

| ID | Nível | Componente(s) | Verificação |
|---|---|---|---|
| RF-01 | Obrigatório | [`routers/recursos.py`](../backend/app/routers/recursos.py), [`services/recursos.py`](../backend/app/services/recursos.py), frontend [`pages/Recursos.tsx`](../frontend/src/pages/Recursos.tsx) | `pytest tests/test_recursos.py::test_cadastro_recurso_aparece_disponivel` |
| RF-02 | Obrigatório | trigger `fn_recursos_valida_estado` + índice `uq_empenho_ativo_por_recurso` ([migração 0001](../backend/alembic/versions/0001_schema_inicial.py)), [`models/enums.py`](../backend/app/models/enums.py) | `pytest tests/test_recursos.py::test_transicao_estado_invalida_e_rejeitada tests/test_empenhos.py::test_duplo_empenho_bloqueado_mesmo_no_banco` |
| RF-03 | Obrigatório | [`services/ocorrencias.py::criar_ocorrencia`](../backend/app/services/ocorrencias.py), frontend [`ModalNovaOcorrencia.tsx`](../frontend/src/components/mapa/ModalNovaOcorrencia.tsx) + [`FerramentaDesenho.tsx`](../frontend/src/components/mapa/FerramentaDesenho.tsx) | `pytest tests/test_ocorrencias.py::test_criar_ocorrencia_com_demandas` |
| RF-04 | Obrigatório | [`services/ocorrencias.py::_demanda_para_out`](../backend/app/services/ocorrencias.py) (cálculo do saldo) | `pytest tests/test_ocorrencias.py::test_saldo_descoberto_diminui_ao_empenhar` |
| RF-05 | Obrigatório | [`services/empenhos.py`](../backend/app/services/empenhos.py), [`routers/empenhos.py`](../backend/app/routers/empenhos.py) | `pytest tests/test_empenhos.py::test_empenhar_e_liberar_ciclo_completo` |
| RF-06 | Desejável | [`services/recursos.py::listar_recursos_compativeis_com_demanda`](../backend/app/services/recursos.py) | `pytest tests/test_ocorrencias.py::test_saldo_descoberto_diminui_ao_empenhar` (verifica também a listagem RF-06) |
| RF-07 | Obrigatório | [`services/recursos.py::listar_recursos`](../backend/app/services/recursos.py) (`lat`/`lon`/`raio_m`) | `pytest tests/test_ocorrencias.py::test_busca_por_raio_e_atributos` |
| RF-08 | Obrigatório | frontend [`pages/Mapa.tsx`](../frontend/src/pages/Mapa.tsx), [`CamadaRecursos.tsx`](../frontend/src/components/mapa/CamadaRecursos.tsx), [`CamadaOcorrencias.tsx`](../frontend/src/components/mapa/CamadaOcorrencias.tsx), [`Legenda.tsx`](../frontend/src/components/mapa/Legenda.tsx) | Manual: abrir `/mapa`, alternar cada camada independentemente, clicar numa feição e conferir o popup de atributos |
| RF-09 | Desejável | [`components/mapa/simbologia.ts`](../frontend/src/components/mapa/simbologia.ts) (forma=tipo via SVG, cor=estado) | Manual: cadastrar recursos de tipos/estados diferentes e conferir no mapa e na legenda |
| RF-10 | Desejável | [`api/hooks.ts`](../frontend/src/api/hooks.ts) (`refetchInterval` de 20s em todas as queries operacionais) | Manual: duas abas logadas, alterar estado numa, observar a outra atualizar em até 60s sem F5 |
| RF-11 | Desejável | [`geoserver/init_geoserver.sh`](../geoserver/init_geoserver.sh), serviço `geoserver` no [`docker-compose.yml`](../docker-compose.yml); acesso pelo proxy com login ([`nginx/nginx.conf`](../nginx/nginx.conf), [`auth/acesso_ogc.py`](../backend/app/auth/acesso_ogc.py)) | `pytest tests/test_acesso_ogc.py`; manual: `curl -k -u "<email>:<senha>" "https://localhost/geoserver/siscoord/wms?service=WMS&version=1.3.0&request=GetCapabilities"` e o equivalente `wfs` (`version=2.0.0`) — confirmar versões 1.3.0/2.0.0 e as camadas `recursos`/`ocorrencias`; sem `-u`, a resposta deve ser `401` |
| RF-12 | Obrigatório | [`auth/dependencias.py`](../backend/app/auth/dependencias.py) (RBAC no backend), [`auth/AuthContext.tsx`](../frontend/src/auth/AuthContext.tsx) + [`Layout.tsx`](../frontend/src/components/Layout.tsx) (ocultar no frontend) | `pytest tests/test_rbac.py tests/test_camadas_externas.py::test_operador_e_consulta_nao_gerenciam_camadas_externas` |
| RF-13 | Obrigatório | triggers `fn_auditoria` (todas as tabelas com escrita pela API) + `REVOKE` em `auditoria` ([migração 0001](../backend/alembic/versions/0001_schema_inicial.py)); trigger em `camadas_externas` ([migração 0002](../backend/alembic/versions/0002_auditoria_camadas_externas.py)); [`routers/auditoria.py`](../backend/app/routers/auditoria.py) (só GET) | `pytest tests/test_auditoria.py tests/test_camadas_externas.py::test_escrita_em_camadas_externas_gera_auditoria` |
| RF-14 | Obrigatório | [`services/relatorios.py`](../backend/app/services/relatorios.py), [`routers/relatorios.py`](../backend/app/routers/relatorios.py) | `pytest tests/test_relatorios.py` |
| RF-15 | Desejável | [`CamadaWMS.tsx::CamadaExternaWMS`](../frontend/src/components/mapa/CamadaWMS.tsx), tela [`pages/CamadasExternas.tsx`](../frontend/src/pages/CamadasExternas.tsx), [`routers/referencia.py`](../backend/app/routers/referencia.py) (`/camadas-externas`), camada de exemplo "Hidrografia (IBGE)" em [`sql/seed_referencia.sql`](../backend/sql/seed_referencia.sql) | `pytest tests/test_camadas_externas.py`; manual: ligar "Hidrografia (IBGE)" no mapa; cadastrar uma URL WMS inválida no menu "Camadas externas", confirmar que o resto do mapa continua funcionando e que o painel mostra "indisponível" |

## Requisitos não funcionais

| ID | Nível | Componente(s) | Verificação |
|---|---|---|---|
| RNF-01 | Obrigatório | um único serviço `postgis` no [`docker-compose.yml`](../docker-compose.yml), usado por `backend` **e** `geoserver` | Manual: conferir que não existe segundo banco/segunda cópia da geometria — ver [arquitetura.md](arquitetura.md) |
| RNF-02 | Obrigatório | colunas `geometry(..., 4674)` na [migração 0001](../backend/alembic/versions/0001_schema_inicial.py); membro `crs` explícito em toda resposta GeoJSON ([`recursos.py`](../backend/app/routers/recursos.py), [`ocorrencias.py`](../backend/app/routers/ocorrencias.py), [`relatorios.py`](../backend/app/services/relatorios.py)) | `pytest tests/test_relatorios.py::test_exportar_geojson_declara_src`; manual: `GetCapabilities` do GeoServer mostra `EPSG:4674` |
| RNF-03 | Obrigatório | GeoServer (OGC WMS/WFS), exportação GeoJSON/GeoPackage ([`services/relatorios.py`](../backend/app/services/relatorios.py)) | `pytest tests/test_relatorios.py::test_exportar_geojson_declara_src tests/test_relatorios.py::test_exportar_geopackage` |
| RNF-04 | Obrigatório | índices GiST (`idx_recursos_geom`, `idx_ocorrencias_geom`) e btree (`idx_recursos_tipo_estado`) na [migração 0001](../backend/alembic/versions/0001_schema_inicial.py) | Manual: gerar massa com `seed_escala.py --recursos 1000`, medir tempo de `/api/recursos?lat=..&lon=..&raio_m=..` (alvo: ≤3s) e do carregamento inicial do mapa com as 6 camadas ligadas (alvo: ≤5s) |
| RNF-05 | Obrigatório | frontend inteiro roda em navegador padrão sem plugin; toda `ErroNegocio` ([`services/erros.py`](../backend/app/services/erros.py)) tem mensagem em português com a ação corretiva | Manual: percorrer o fluxo CEN-1 (cadastrar ocorrência → ver demanda → empenhar recurso) e contar interações (alvo: ≤5); provocar cada erro de negócio e conferir a mensagem |
| RNF-06 | Obrigatório | TLS no [`nginx/nginx.conf`](../nginx/nginx.conf); portas 8000/8080 publicadas só em `127.0.0.1` no [`docker-compose.yml`](../docker-compose.yml); hash bcrypt (sal embutido) em [`auth/seguranca.py`](../backend/app/auth/seguranca.py); procedimento de backup/restauração no [manual de instalação](manual-instalacao.md) | Manual: seguir o par backup→restauração do manual e conferir contagem de linhas antes/depois; de **outra** máquina, confirmar que `http://<servidor>:8000` e `:8080` recusam conexão e que `http://<servidor>` redireciona para HTTPS |
| RNF-07 | Obrigatório | [`docker-compose.yml`](../docker-compose.yml) + [manual-instalacao.md](manual-instalacao.md) | Manual: seguir o manual do zero numa máquina limpa e cronometrar |
| RNF-08 | Obrigatório | esta pasta `docs/` inteira | Checklist: [arquitetura](arquitetura.md) ✓, [modelo de dados](modelo-dados.md) ✓, UML — [casos de uso](uml/casos-de-uso.md) ✓ [classes](uml/classes.md) ✓ [sequência](uml/sequencia-empenho.md) ✓ [implantação](uml/implantacao.md) ✓, [manual de instalação](manual-instalacao.md) ✓, esta matriz ✓ |
| RNF-09 | Obrigatório | [`LICENSE`](../LICENSE) (MIT); [conformidade.md](conformidade.md) (IDE-Defesa/LGPD); regras de acesso às camadas OGC ([`auth/acesso_ogc.py`](../backend/app/auth/acesso_ogc.py) + `auth_request` no [`nginx/nginx.conf`](../nginx/nginx.conf)) | Manual: conferir que toda dependência em [`backend/requirements.txt`](../backend/requirements.txt)/[`frontend/package.json`](../frontend/package.json) e toda imagem no `docker-compose.yml` é software livre — ver [conformidade.md](conformidade.md) |
| RNF-10 | Desejável | [`seed/seed_escala.py`](../backend/app/seed/seed_escala.py) | Manual: `docker compose exec backend python -m app.seed.seed_escala --recursos 600 --ocorrencias 25`, depois teste de carga com 20 sessões simultâneas (ferramenta a critério da equipe — ex.: `k6`, `locust`) |

## Cobertura de testes automatizados

```
backend/tests/
├── test_recursos.py          RF-01, RF-02
├── test_empenhos.py          RF-02, RF-05, OBJ-3 (inclui teste contra o banco, não só a API)
├── test_ocorrencias.py       RF-03, RF-04, RF-06, RF-07
├── test_rbac.py              RF-12
├── test_auditoria.py         RF-13
├── test_camadas_externas.py  RF-15, RF-13 (trilha em camadas_externas), RF-12
├── test_acesso_ogc.py        RF-11 / RNF-09 (login exigido para WMS/WFS)
└── test_relatorios.py        RF-14, RNF-02, RNF-03
```

Requisitos de UX/performance/implantação (RF-08, RF-09, RF-10, RNF-04 a
RNF-10) e a parte visual/integrada de RF-11 e RF-15 (tiles no mapa, provedor
fora do ar, `GetCapabilities` pelo proxy) são verificados por procedimento manual porque medem
propriedades de interface, tempo de resposta em carga, ou o processo de
implantação em si — não fazem sentido como asserção unitária. O
procedimento de cada um está descrito na coluna "Verificação" acima.

## Definição de pronto (conforme o documento de requisitos)

> Um requisito só conta como atendido quando está operante no ambiente de
> homologação (não só na máquina do desenvolvedor), consta desta matriz com
> componente e caso de teste, e é reproduzível por terceiro apenas com a
> documentação.

Antes de marcar qualquer linha acima como "pronta" para a banca/homologação,
confirme as três condições contra uma implantação feita do zero seguindo
[manual-instalacao.md](manual-instalacao.md) — não contra o ambiente onde o
código foi escrito.

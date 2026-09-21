# Termo de Abertura do Projeto (TAP)

| Campo | Valor |
|---|---|
| Projeto | SISCOORD-DC — Sistema de Coordenação Geoespacial de Recursos de Defesa Civil |
| Demandante | Defesa Civil Estadual, em conjunto com o Exército Brasileiro |
| Equipe | Desenvolvimento (9 alunos) · Stakeholders (3) · Auditores (3) |
| Emissor dos requisitos | Stakeholders — Documento de Requisitos v2.0 |
| Gerente do projeto | _(preencher)_ |
| Repositório | <https://github.com/viniciusbrito1/GeoProjeto_SIG> |
| Data da linha de base | 03/08/2026 |
| Versão deste termo | 1.1 — 21/09/2026 |

## 1. Justificativa

Municípios atingidos por chuvas acima da média precisam de equipes,
instalações (abrigos, bases) e equipamentos (viaturas, bombas, embarcações)
vindos de vários órgãos — Defesa Civil, Corpo de Bombeiros, Exército, Polícia
Militar, SAMU. Sem um sistema comum, a coordenação depende de telefone e
planilhas: cada órgão enxerga uma situação diferente, o mesmo meio pode ser
prometido para duas missões, outro fica ocioso sem ninguém saber, e não fica
registro de quem decidiu o quê.

O SISCOORD-DC centraliza essa coordenação num mapa único, com o estado de cada
recurso, as ocorrências e o que ainda falta atender em cada uma.

## 2. Objetivos (do Documento de Requisitos v2.0)

| ID | Objetivo | Indicador de sucesso |
|---|---|---|
| OBJ-1 | Empenhar o meio certo, mais rápido | tarefa completa em ≤ 5 interações; consulta em ≤ 3 s |
| OBJ-2 | Todos vendo a mesma situação | alteração aparece em outra sessão em ≤ 60 s |
| OBJ-3 | Nenhum meio duplicado ou ocioso | duplo empenho impossível pelo sistema |
| OBJ-4 | Decisões rastreáveis, dados interoperáveis | trilha de auditoria completa; camadas em WMS/WFS |

## 3. Escopo

### 3.1 Dentro do escopo

- Aplicação web com os 25 requisitos do Documento de Requisitos v2.0
  (15 funcionais, 10 não funcionais) — detalhados na
  [matriz de rastreabilidade](../matriz-rastreabilidade.md).
- Cadastro georreferenciado de recursos; ocorrências com área atingida em
  polígono; demandas e saldo descoberto; empenho e liberação com autor e
  data-hora.
- Mapa interativo com camadas, simbologia por tipo e estado e atualização
  entre sessões.
- Publicação WMS 1.3.0 / WFS 2.0.0 e consumo de WMS externo.
- Autenticação com três perfis (Coordenador, Operador, Consulta) e trilha de
  auditoria não editável.
- SITREP em PDF e exportação em GeoJSON e GeoPackage.
- Implantação por Docker Compose com HTTPS, backup e restauração.
- Documentação técnica exigida pelo RNF-08 e esta documentação de gestão.

### 3.2 Fora do escopo

- Cadastro de vítimas, moradores ou qualquer civil identificável (LGPD — ver
  [conformidade.md](../conformidade.md)).
- Aplicativo móvel nativo (o sistema roda em navegador).
- Integração automática com sistemas de outros órgãos além de WMS/WFS.
- Hospedagem e operação em produção após a decisão de 05/10/2026.
- Certificado TLS emitido por autoridade certificadora (fica a cargo do órgão;
  o projeto entrega certificado autoassinado para homologação).
- Carga completa da tabela de municípios do IBGE (o projeto entrega uma
  amostra do Espírito Santo; ver `backend/sql/seed_referencia.sql`).

## 4. Principais entregas

| Entrega | Descrição |
|---|---|
| E1 | Código-fonte completo (backend, frontend, GeoServer, proxy, scripts) com licença livre |
| E2 | Ambiente implantável com um comando (`docker compose up`) |
| E3 | Testes automatizados + roteiro de verificação manual |
| E4 | Documentação técnica (RNF-08): arquitetura, modelo de dados, UML, manual de instalação, matriz de rastreabilidade |
| E5 | Documentação de gestão (esta pasta) |
| E6 | Demonstração em homologação e pacote de entrega (29/09/2026) |

A decomposição completa está na [EAP](eap.md).

## 5. Marcos

| Marco | Data |
|---|---|
| M0 — Requisitos definidos pelos Stakeholders | 03/08/2026 |
| M1 — Indicadores de auditoria definidos pelos Auditores | 13/08/2026 |
| M2 — Sprint parcial 1 (andamento + julgamento de mudanças) | 15/09/2026 |
| M3 — Sprint parcial 2 (andamento + julgamento de mudanças) | 22/09/2026 |
| M4 — **Entrega e auditoria** | **29/09/2026** |
| M5 — **Parecer de conformidade e aprovação/reprovação** | **05/10/2026** |

Cronograma detalhado: [cronograma.md](cronograma.md).

## 6. Premissas

- O Documento de Requisitos v2.0 é a linha de base; mudanças seguem o
  [controle de mudanças](controle-mudancas.md).
- Existe uma máquina de homologação com Docker, pelo menos 2 vCPU, 4 GB de RAM
  e 10 GB livres (ver [implantacao.md](../uml/implantacao.md)).
- A máquina de homologação tem acesso à internet para baixar as imagens
  Docker e os mapas-base.
- Os Auditores definem os indicadores de avaliação em 13/08 e auditam a
  entrega em 29/09 com base neles.
- Os integrantes da equipe estão disponíveis até a decisão de 05/10/2026.

## 7. Restrições

- **Prazo fixo:** sprints parciais em 15/09 e 22/09, entrega em 29/09/2026 e parecer/decisão em 05/10/2026.
- **Somente software livre** com licença declarada (RNF-09).
- **Arquitetura integrada:** geometria e atributos no mesmo SGBD; arquitetura
  dual é vedada (RNF-01).
- **SIRGAS 2000 (EPSG:4674)** como referência de armazenamento (RNF-02).
- **Padrões abertos OGC**; nenhuma saída só em formato proprietário (RNF-03).
- **Conformidade** com a Portaria GM-MD nº 2.445/2021 (IDE-Defesa) e com a LGPD (RNF-09).
- **Orçamento:** sem custo de licenças de software; custo do projeto limitado
  às horas da equipe e à infraestrutura de homologação.

## 8. Critérios de sucesso e aceite

O projeto é aceito quando, na data de entrega:

1. Os **19 requisitos obrigatórios** atendem à *definição de pronto* do
   Documento de Requisitos: operam no ambiente de homologação, constam da
   matriz de rastreabilidade com componente e caso de teste, e um terceiro
   consegue reproduzir usando só a documentação.
2. Os 6 requisitos desejáveis entregues também atendem à definição de pronto
   (os que não forem entregues ficam registrados no relatório de situação).
3. Um terceiro sobe o sistema em máquina limpa em ≤ 60 minutos (RNF-07).
4. A documentação exigida pelo RNF-08 está completa.

## 9. Riscos de alto nível

Detalhados no [registro de riscos](riscos.md). Os principais são: tempo curto
para homologação entre o fim do desenvolvimento e a entrega; conhecimento
técnico concentrado em uma pessoa; implantação em máquina limpa passar dos 60
minutos; e verificações manuais sem evidência registrada.

## 10. Project Model Canvas

| Pergunta | Resposta |
|---|---|
| **Por quê?** — Justificativa | coordenação entre órgãos por telefone e planilha; meios duplicados ou ociosos; decisões sem registro |
| **Por quê?** — Objetivo SMART | entregar até 29/09/2026 um sistema web que atenda aos 19 requisitos obrigatórios do Documento v2.0, verificados em homologação |
| **Por quê?** — Benefícios | empenho mais rápido; mesma situação para todos; nenhum duplo empenho; auditoria e interoperabilidade com a IDE-Defesa |
| **O quê?** — Produto | aplicação web geoespacial (mapa, recursos, ocorrências, empenhos, SITREP, WMS/WFS) |
| **O quê?** — Requisitos | 25 requisitos (15 RF, 10 RNF) — [matriz](../matriz-rastreabilidade.md) |
| **Quem?** — Stakeholders | Defesa Civil Estadual, Exército Brasileiro, Stakeholders, Auditores, órgãos de origem dos recursos, usuários (Coordenador, Operador, Consulta) |
| **Quem?** — Equipe | Gerente de Projeto, Desenvolvedor Backend, Desenvolvedor Frontend/SIG, Infraestrutura, Qualidade, Documentação ([papéis](organizacao-raci.md)) |
| **Como?** — Premissas | requisitos estáveis; máquina de homologação disponível; Auditores disponíveis |
| **Como?** — Grupos de entrega | gestão · requisitos · arquitetura e dados · backend · frontend e mapa · interoperabilidade · segurança e conformidade · qualidade · implantação · documentação · homologação ([EAP](eap.md)) |
| **Como?** — Restrições | prazo fixo; software livre; um SGBD só; SIRGAS 2000; padrões OGC; LGPD |
| **Quando e quanto?** — Riscos | ver seção 9 e [riscos.md](riscos.md) |
| **Quando e quanto?** — Linha do tempo | 03/08 requisitos · 13/08 indicadores · 15/09 e 22/09 sprints parciais · 29/09 entrega e auditoria · 05/10 parecer e decisão |
| **Quando e quanto?** — Custos | licenças: R$ 0 (software livre); horas da equipe; 1 servidor de homologação |

## 11. Aprovação

| Papel | Nome | Assinatura | Data |
|---|---|---|---|
| Patrocinador (Defesa Civil Estadual) | | | |
| Representante do Exército Brasileiro | | | |
| Gerente do projeto | | | |

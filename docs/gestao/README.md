# Gestão do projeto SISCOORD-DC

Documentação de gerenciamento do projeto (escopo, tempo, riscos, partes
interessadas, comunicação e controle). Complementa a documentação técnica
exigida pelo RNF-08 (ver [`docs/`](../)), que descreve o *produto*; esta pasta
descreve o *projeto* que o entrega.

Os diagramas estão em Mermaid — renderizam direto no GitHub/GitLab e no VS Code
(extensão "Markdown Preview Mermaid Support").

## Dados de referência do projeto

| Item | Valor |
|---|---|
| Projeto | SISCOORD-DC — Sistema de Coordenação Geoespacial de Recursos de Defesa Civil |
| Repositório | <https://github.com/viniciusbrito1/GeoProjeto_SIG> |
| Demandantes | Defesa Civil Estadual · Exército Brasileiro |
| Documento de requisitos | Lista de Requisitos v2.0, emitida pelos Stakeholders em 03/08/2026 |
| Linha de base | 03/08/2026 |
| Entrega | 29/09/2026 |
| Indicadores de auditoria | 13/08/2026 |
| Sprints parciais | 15/09 e 22/09/2026 |
| Parecer e decisão | 05/10/2026 |
| Equipe | Desenvolvimento: 9 alunos · Stakeholders: 3 · Auditores: 3 |
| Escopo contratado | 25 requisitos (15 funcionais · 10 não funcionais; 19 obrigatórios · 6 desejáveis) |
| Situação em 21/09/2026 | desenvolvimento concluído · verificação contra os indicadores ([relatório](status-projeto.md)) |

## Documentos

| # | Documento | Conteúdo | Diagramas |
|---|---|---|---|
| 1 | [Termo de abertura](termo-abertura.md) | justificativa, objetivos, escopo, premissas, restrições, marcos, critérios de sucesso, Project Model Canvas | — |
| 2 | [EAP e dicionário da EAP](eap.md) | decomposição do escopo em pacotes de trabalho, com entregável, critério de aceite, requisito e situação de cada um | **EAP** |
| 3 | [Cronograma](cronograma.md) | atividades, dependências, marcos e caminho crítico | **Gantt**, **diagrama de rede (caminho crítico)** |
| 4 | [Organização e responsabilidades](organizacao-raci.md) | papéis, organograma do projeto, matriz RACI | **Organograma**, **RACI** |
| 5 | [Partes interessadas e comunicação](partes-interessadas.md) | registro de partes interessadas, estratégia de engajamento, plano de comunicação | **Matriz poder × interesse** |
| 6 | [Riscos](riscos.md) | registro de riscos com probabilidade, impacto, resposta e dono | **Matriz de probabilidade × impacto** |
| 7 | [Controle de mudanças](controle-mudancas.md) | como uma alteração de escopo é pedida, analisada e aprovada | **Fluxo de controle de mudanças** |
| 8 | [Relatório de situação](status-projeto.md) | onde o projeto está em 21/09/2026, pendências para a entrega e questões em aberto | **Semáforo**, **cobertura de verificação** |

## Como manter

- **Semanalmente:** atualizar o [relatório de situação](status-projeto.md), a
  coluna "Situação" do [dicionário da EAP](eap.md) e o [registro de riscos](riscos.md).
- **A cada mudança de escopo aprovada:** seguir o [controle de mudanças](controle-mudancas.md)
  e atualizar EAP, cronograma e [matriz de rastreabilidade](../matriz-rastreabilidade.md)
  juntos — os três precisam contar a mesma história.
- **Nomes dos integrantes:** os documentos usam *papéis* (Gerente de Projeto,
  Desenvolvedor Backend etc.). Preencha quem ocupa cada papel na tabela de
  [organizacao-raci.md](organizacao-raci.md#papéis-e-integrantes); uma mesma pessoa
  pode acumular papéis.

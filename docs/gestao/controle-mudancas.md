# Controle integrado de mudanças

A linha de base de escopo é o **Documento de Requisitos v2.0 (03/08/2026)**,
decomposto na [EAP](eap.md). Qualquer alteração em requisito, escopo, prazo ou
critério de aceite passa por este fluxo antes de virar código.

**O que não passa por aqui:** correção de defeito que faz o sistema cumprir um
requisito que *já* estava na linha de base (por exemplo, os riscos R07, R09 e
R14 em [riscos.md](riscos.md)). Isso é trabalho da EAP 1.8/1.11 e segue direto
para correção, só com registro no relatório de situação.

## Fluxo

```mermaid
flowchart TD
    classDef inicio fill:#1f3d5c,stroke:#1f3d5c,color:#ffffff
    classDef decisao fill:#fff4e5,stroke:#b9770e,color:#1a1a1a
    classDef acao fill:#eef3f8,stroke:#2f6690,color:#1a1a1a
    classDef fim fill:#e8f5e9,stroke:#2e7d32,color:#1a1a1a
    classDef rejeita fill:#fde8e8,stroke:#c0392b,color:#1a1a1a

    S(["Solicitação de mudança<br/>(qualquer parte interessada)"]):::inicio
    R["GP registra a solicitação<br/>com ID SM-nn"]:::acao
    T{"É defeito contra<br/>requisito da linha de base?"}:::decisao
    DEF["Tratar como correção<br/>(EAP 1.8 / 1.11)"]:::fim
    A["Análise de impacto pela equipe<br/>• requisitos afetados (matriz de rastreabilidade)<br/>• pacotes da EAP<br/>• dias no caminho crítico<br/>• novos riscos"]:::acao
    CC{"Consome folga do<br/>caminho crítico ou<br/>muda requisito obrigatório?"}:::decisao
    GPD{"GP aprova?"}:::decisao
    PD{"Patrocinador + Grupo<br/>Stakeholders aprovam?"}:::decisao
    AT["Atualizar linhas de base juntas:<br/>EAP · cronograma · matriz de rastreabilidade · riscos"]:::acao
    IMPL["Implementar, testar e<br/>registrar evidência"]:::acao
    COM["Comunicar partes interessadas<br/>(relatório de situação)"]:::fim
    REJ["Rejeitar ou adiar<br/>(registrar motivo)"]:::rejeita

    S --> R --> T
    T -- sim --> DEF
    T -- não --> A --> CC
    CC -- não --> GPD
    CC -- sim --> PD
    GPD -- sim --> AT
    GPD -- não --> REJ
    PD -- sim --> AT
    PD -- não --> REJ
    AT --> IMPL --> COM
    REJ --> COM
```

## Alçadas de aprovação

| Tipo de mudança | Quem aprova |
|---|---|
| Ajuste interno sem efeito em requisito, prazo ou caminho crítico (ex.: reordenar atividades com folga) | Gerente de Projeto |
| Mudança em requisito **desejável**, ou que consome folga de atividade fora do caminho crítico | Gerente de Projeto, informando os Stakeholders |
| Mudança em requisito **obrigatório**, na data de entrega, ou que consome o caminho crítico | Stakeholders (julgamento nas sprints de 15/09 e 22/09) |

**Congelamento de escopo:** a partir da **sprint parcial 1 (15/09/2026)** (fim do
desenvolvimento), só entram mudanças que corrijam defeito ou que o
patrocinador classifique como impeditivas para a decisão.

## Formulário de solicitação de mudança

Copie o bloco abaixo para uma *issue* no repositório ou para o registro de
mudanças.

```text
ID: SM-__
Data:                         Solicitante:
Tipo: [ ] requisito  [ ] escopo  [ ] prazo  [ ] critério de aceite
Descrição da mudança:
Justificativa:

--- Análise de impacto (equipe) ---
Requisitos afetados (RF/RNF):
Pacotes da EAP afetados:
Esforço estimado (dias úteis):
Efeito no caminho crítico:   [ ] nenhum  [ ] consome folga  [ ] atrasa entrega
Novos riscos:

--- Decisão ---
[ ] aprovada  [ ] rejeitada  [ ] adiada      Por:            Data:
Motivo:
Documentos atualizados: [ ] EAP [ ] cronograma [ ] matriz de rastreabilidade [ ] riscos
```

## Registro de mudanças

| ID | Data | Solicitante | Descrição | Impacto | Decisão | Data da decisão |
|---|---|---|---|---|---|---|
| — | — | — | nenhuma mudança de escopo aprovada nas sprints; as correções de 15 a 18/09 foram defeitos contra a linha de base | — | — | — |

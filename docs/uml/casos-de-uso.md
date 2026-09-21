# Diagrama de casos de uso

Mermaid não tem um tipo nativo de diagrama de casos de uso UML; a notação
abaixo usa um fluxograma. Os casos de uso estão agrupados por **quem pode
executá-los**: a seta de um ator para um grupo significa que ele executa todos
os casos de uso daquele grupo.

```mermaid
flowchart TB
    classDef ator fill:#1f3d5c,stroke:#1f3d5c,color:#ffffff,font-weight:bold
    classDef uc fill:#ffffff,stroke:#2f6690,color:#1a1a1a

    Coordenador(["👤 Coordenador<br/>escrita total"]):::ator
    Operador(["👤 Operador<br/>escrita restrita"]):::ator
    Consulta(["👤 Consulta<br/>somente leitura"]):::ator

    subgraph SC["Somente Coordenador"]
        direction TB
        UC1(["Cadastrar / alterar recurso · RF-01"]):::uc ~~~ UC2(["Inativar recurso · RF-01"]):::uc
        UC2 ~~~ UC16(["Gerenciar usuários e perfis · RF-12"]):::uc
        UC16 ~~~ UC17(["Gerenciar camadas WMS externas · RF-15"]):::uc
        UC17 ~~~ UC15(["Consultar trilha de auditoria · RF-13"]):::uc
    end
    subgraph CO["Coordenador e Operador"]
        direction TB
        UC3(["Registrar ocorrência · RF-03"]):::uc ~~~ UC4(["Registrar demanda · RF-04"]):::uc
        UC4 ~~~ UC11(["Listar compatíveis com demanda · RF-06"]):::uc
        UC11 ~~~ UC5(["Empenhar recurso · RF-05"]):::uc
        UC5 ~~~ UC6(["Liberar recurso · RF-05"]):::uc
        UC6 ~~~ UC7(["Mudar estado operacional · RF-02"]):::uc
        UC7 ~~~ UC8(["Encerrar ocorrência"]):::uc
    end
    subgraph TODOS["Todos os perfis"]
        direction TB
        UC9(["Ver mapa interativo · RF-08/09/10"]):::uc ~~~ UC10(["Buscar por raio e atributos · RF-07"]):::uc
        UC10 ~~~ UC12(["Gerar SITREP · RF-14"]):::uc
        UC12 ~~~ UC13(["Exportar camadas · RF-14"]):::uc
        UC13 ~~~ UC14(["Consumir WMS externo · RF-15"]):::uc
    end

    Coordenador --> SC
    Coordenador --> CO
    Coordenador --> TODOS
    Operador --> CO
    Operador --> TODOS
    Consulta --> TODOS
```

## Atores

| Ator | Descrição |
|---|---|
| **Coordenador** | escrita total (RF-12): cadastro mestre de recursos, gestão de usuários, auditoria, e tudo que o Operador faz |
| **Operador** | escrita restrita às operações de campo: ocorrências, demandas, empenho/liberação, mudança de estado operacional |
| **Consulta** | somente leitura: mapa, buscas, relatórios — nenhuma ação de escrita |

## Caso de uso principal: empenhar recurso (CEN-1)

1. Operador (ou Coordenador) abre uma ocorrência com demanda descoberta.
2. Sistema lista recursos disponíveis e compatíveis, ordenados por distância (RF-06).
3. Usuário escolhe um recurso e confirma o empenho.
4. Sistema registra o empenho (autor, data/hora), muda o estado do recurso
   para "empenhado" e atualiza o saldo da demanda — tudo em uma única
   transação (RF-05).
5. Em até 5 interações a partir da tela de demandas (RNF-05) e refletido em
   qualquer outra sessão conectada em até 60s (RF-10, OBJ-2).

Este é o fluxo detalhado, passo a passo técnico, em
[sequencia-empenho.md](sequencia-empenho.md).

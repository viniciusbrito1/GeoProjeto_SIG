# Diagramas de sequência

Cada linha de vida é um **objeto de uma classe do [diagrama de classes](classes.md)**
(`Usuario`, `Ocorrencia`, `Demanda`, `Recurso`, `Empenho`, `Auditoria`), no
formato `objeto: Classe`. As mensagens são operações dessas classes
(`saldo_descoberto()`, `alterar_estado()`, `liberar()`, criação de objeto) e
só percorrem associações que existem no diagrama de classes:

| Mensagem | Associação usada (diagrama de classes) |
|---|---|
| `operador` cria (`«create»`) `e: Empenho` | Usuario **autoriza** Empenho (1 : 0..*) |
| `o` consulta `d.saldo_descoberto()` | Ocorrencia **tem** Demanda (1 : 0..*) |
| `e` chama `r.alterar_estado()` | Recurso **é empenhado em** Empenho (1 : 0..*) |
| `e` se vincula a `o` e a `d` | Ocorrencia **recebe** Empenho · Demanda **cobre** Empenho |
| `operador` gera (`«create»`) `a1`, `a2: Auditoria` | Usuario **gera** Auditoria (0..1 : 0..*) |

## 1. Empenhar um recurso (RF-05)

O operador é um `Usuario` com perfil `operador` (o ator do caso de uso
*Empenhar recurso*).

```mermaid
sequenceDiagram
    actor U as operador: Usuario
    participant O as o: Ocorrencia
    participant D as d: Demanda
    participant R as r: Recurso

    U->>O: status
    O-->>U: aberta
    U->>O: demandas
    O->>D: saldo_descoberto()
    D-->>O: 2
    O-->>U: d (saldo descoberto 2)
    U->>R: estado
    R-->>U: disponivel
    create participant E as e: Empenho
    U->>E: «create» Empenho(recurso = r, ocorrencia = o, demanda = d, autor_empenho = operador)
    Note over E,R: invariante: no máximo 1 Empenho ativo por Recurso
    E->>R: alterar_estado(empenhado)
    R-->>E: estado = empenhado
    E-->>U: status = ativo, empenhado_em = agora
    create participant A1 as a1: Auditoria
    U->>A1: «create» Auditoria(tabela = empenhos, operacao = INSERT)
    create participant A2 as a2: Auditoria
    U->>A2: «create» Auditoria(tabela = recursos, operacao = UPDATE)
    U->>O: demandas
    O->>D: saldo_descoberto()
    D-->>O: 1
    O-->>U: d (saldo descoberto 1)
```

Leitura: o operador confere que a ocorrência está aberta, que a demanda ainda
tem saldo descoberto e que o recurso está disponível; cria o `Empenho`, que
leva o `Recurso` para `empenhado`; cada escrita gera um registro de `Auditoria`
(`a1`, `a2`) em nome do operador; o saldo descoberto da demanda cai de 2 para 1.

## 2. Duplo empenho concorrente (OBJ-3)

Dois operadores tentam empenhar o **mesmo** recurso quase ao mesmo tempo.

```mermaid
sequenceDiagram
    actor UA as operadorA: Usuario
    actor UB as operadorB: Usuario
    participant R as r: Recurso

    UA->>R: estado
    R-->>UA: disponivel
    UB->>R: estado
    R-->>UB: disponivel
    create participant E1 as e1: Empenho
    UA->>E1: «create» Empenho(recurso = r, autor_empenho = operadorA)
    E1->>R: alterar_estado(empenhado)
    R-->>E1: estado = empenhado
    E1-->>UA: status = ativo
    create participant E2 as e2: Empenho
    UB->>E2: «create» Empenho(recurso = r, autor_empenho = operadorB)
    Note over E2,R: violaria a invariante — r já tem um Empenho ativo (e1)
    destroy E2
    E2--xUB: recusado: "Recurso já foi empenhado. Escolha outro."
```

As duas leituras de `estado` devolvem `disponivel`, mas quem decide é a
**invariante** "no máximo 1 `Empenho` ativo por `Recurso`", verificada no
momento da criação do empenho — não a leitura anterior. Por isso `e2` nunca
chega a existir e o operador B recebe a mensagem com a ação corretiva
(RNF-05).

## Como as operações são garantidas na implementação

| Operação / regra (diagramas) | Onde é garantida |
|---|---|
| criar `Empenho` | `services/empenhos.py::empenhar_recurso` (`POST /api/empenhos`) |
| invariante "1 `Empenho` ativo por `Recurso`" | índice único parcial `uq_empenho_ativo_por_recurso` no banco |
| `Recurso.alterar_estado()` | serviço + trigger `trg_recursos_valida_estado` (rejeita transição inválida) |
| `Demanda.saldo_descoberto()` | `services/ocorrencias.py::_demanda_para_out` |
| gerar `Auditoria` | trigger `fn_auditoria()` em cada escrita, com o usuário da sessão |

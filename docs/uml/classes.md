# Diagrama de classes

Reflete os modelos SQLAlchemy em [`backend/app/models/`](../../backend/app/models/),
que espelham o schema do banco. Este diagrama e o [diagrama ER](../modelo-dados.md)
são gerados da **mesma definição do modelo**: cada classe corresponde a uma
tabela, com os mesmos atributos, relacionamentos e cardinalidades (tabela de
correspondência em [modelo-dados.md](../modelo-dados.md)).

```mermaid
classDiagram
    class Usuario {
        +UUID id
        +str nome
        +str email
        +str senha_hash
        +PerfilUsuario perfil
        +bool ativo
        +datetime criado_em
    }
    class Orgao {
        +UUID id
        +str nome
        +str sigla
    }
    class Municipio {
        +str codigo_ibge
        +str nome
        +str uf
    }
    class Recurso {
        +UUID id
        +TipoRecurso tipo
        +str nome
        +UUID orgao_id
        +str especialidade
        +Decimal capacidade_valor
        +str capacidade_unidade
        +Point geom
        +EstadoRecurso estado
        +bool ativo
        +datetime criado_em
        +datetime atualizado_em
        +alterar_estado(novo_estado)
    }
    class Ocorrencia {
        +UUID id
        +str tipo
        +SeveridadeOcorrencia severidade
        +str municipio_codigo_ibge
        +MultiPolygon area_atingida
        +str descricao
        +StatusOcorrencia status
        +UUID criado_por
        +datetime criado_em
        +datetime encerrado_em
        +encerrar()
    }
    class Demanda {
        +UUID id
        +UUID ocorrencia_id
        +TipoRecurso tipo_recurso
        +str especialidade
        +int quantidade_necessaria
        +datetime criado_em
        +saldo_descoberto() int
    }
    class Empenho {
        +UUID id
        +UUID recurso_id
        +UUID ocorrencia_id
        +UUID demanda_id
        +StatusEmpenho status
        +UUID autor_empenho_id
        +datetime empenhado_em
        +UUID autor_liberacao_id
        +datetime liberado_em
        +liberar()
    }
    class Auditoria {
        +int id
        +str tabela
        +str operacao
        +UUID registro_id
        +UUID usuario_id
        +dict dados_antes
        +dict dados_depois
        +datetime criado_em
    }
    class CamadaExterna {
        +UUID id
        +str nome
        +str url_wms
        +str nome_camada
        +bool ativa
        +datetime criado_em
    }
    class PerfilUsuario {
        <<enumeration>>
        coordenador
        operador
        consulta
    }
    class TipoRecurso {
        <<enumeration>>
        equipe
        instalacao
        equipamento
    }
    class EstadoRecurso {
        <<enumeration>>
        disponivel
        empenhado
        indisponivel
        inativo
    }
    class SeveridadeOcorrencia {
        <<enumeration>>
        baixa
        media
        alta
        critica
    }
    class StatusOcorrencia {
        <<enumeration>>
        aberta
        encerrada
    }
    class StatusEmpenho {
        <<enumeration>>
        ativo
        liberado
    }
    Orgao "1" --> "0..*" Recurso : origem de
    Municipio "1" --> "0..*" Ocorrencia : localiza
    Usuario "1" --> "0..*" Ocorrencia : abre
    Ocorrencia "1" --> "0..*" Demanda : tem
    Ocorrencia "1" --> "0..*" Empenho : recebe
    Demanda "0..1" --> "0..*" Empenho : cobre
    Recurso "1" --> "0..*" Empenho : é empenhado em
    Usuario "1" --> "0..*" Empenho : autoriza
    Usuario "0..1" --> "0..*" Empenho : libera
    Usuario "0..1" --> "0..*" Auditoria : gera (via trigger)
    Usuario ..> PerfilUsuario
    Recurso ..> TipoRecurso
    Demanda ..> TipoRecurso
    Recurso ..> EstadoRecurso
    Ocorrencia ..> SeveridadeOcorrencia
    Ocorrencia ..> StatusOcorrencia
    Empenho ..> StatusEmpenho
```

## Notas de desenho

- `Recurso.alterar_estado()` e `Ocorrencia.encerrar()` estão representados
  como métodos de domínio para legibilidade do diagrama, mas na
  implementação vivem na camada de serviço
  ([`backend/app/services/`](../../backend/app/services/)) — os modelos
  SQLAlchemy em si são anêmicos (armazenam estado, não comportamento). A
  regra que esses métodos protegem é reforçada de novo no banco (trigger +
  constraint), então a "lógica" real não depende de nenhuma dessas duas
  camadas isoladamente.
- `Auditoria` não aparece com métodos de escrita porque não tem nenhum — é
  populada só pelo trigger `fn_auditoria()` (ver
  [modelo-dados.md](../modelo-dados.md)), nunca pela camada de aplicação.
  O vínculo *Usuario gera Auditoria* é 0..1 porque `usuario_id` é uma
  referência **lógica** (sem constraint de chave estrangeira): o trigger grava
  a trilha mesmo quando a escrita não vem de um usuário autenticado.
- `Empenho` tem dois vínculos com `Usuario`: quem **autoriza** o empenho
  (sempre existe, 1) e quem **libera** (só existe depois da liberação, 0..1).
- Um `Empenho` é imutável quanto ao vínculo `Recurso`↔`Ocorrencia`: para
  mudar de recurso, libera-se o empenho atual e cria-se outro. Isso mantém o
  histórico (RF-05) sempre correto.

import enum


class PerfilUsuario(str, enum.Enum):
    coordenador = "coordenador"
    operador = "operador"
    consulta = "consulta"


class TipoRecurso(str, enum.Enum):
    equipe = "equipe"
    instalacao = "instalacao"
    equipamento = "equipamento"


class EstadoRecurso(str, enum.Enum):
    disponivel = "disponivel"
    empenhado = "empenhado"
    indisponivel = "indisponivel"
    inativo = "inativo"


class SeveridadeOcorrencia(str, enum.Enum):
    baixa = "baixa"
    media = "media"
    alta = "alta"
    critica = "critica"


class StatusOcorrencia(str, enum.Enum):
    aberta = "aberta"
    encerrada = "encerrada"


class StatusEmpenho(str, enum.Enum):
    ativo = "ativo"
    liberado = "liberado"


# Transições de estado permitidas para `recursos.estado` (RF-02).
# Espelhada pelo trigger `trg_recursos_valida_estado` no banco — a validação
# aqui existe só para devolver uma mensagem em português (RNF-05) antes de
# bater no banco; quem garante a regra de verdade é o trigger.
TRANSICOES_ESTADO_VALIDAS: dict[EstadoRecurso, set[EstadoRecurso]] = {
    EstadoRecurso.disponivel: {EstadoRecurso.empenhado, EstadoRecurso.indisponivel, EstadoRecurso.inativo},
    EstadoRecurso.empenhado: {EstadoRecurso.disponivel},
    EstadoRecurso.indisponivel: {EstadoRecurso.disponivel, EstadoRecurso.inativo},
    EstadoRecurso.inativo: {EstadoRecurso.disponivel},
}

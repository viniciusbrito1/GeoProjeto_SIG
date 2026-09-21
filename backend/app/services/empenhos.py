import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.empenho import Empenho
from app.models.enums import EstadoRecurso, StatusEmpenho, StatusOcorrencia
from app.models.ocorrencia import Demanda, Ocorrencia
from app.models.recurso import Recurso
from app.schemas.empenho import EmpenhoCreate, EmpenhoOut
from app.services.erros import ErroNegocio


def _para_out(empenho: Empenho, recurso_nome: str | None = None) -> EmpenhoOut:
    return EmpenhoOut(
        id=empenho.id,
        recurso_id=empenho.recurso_id,
        recurso_nome=recurso_nome,
        ocorrencia_id=empenho.ocorrencia_id,
        demanda_id=empenho.demanda_id,
        status=empenho.status,
        autor_empenho_id=empenho.autor_empenho_id,
        empenhado_em=empenho.empenhado_em,
        autor_liberacao_id=empenho.autor_liberacao_id,
        liberado_em=empenho.liberado_em,
    )


def empenhar_recurso(db: Session, dados: EmpenhoCreate, autor_id: uuid.UUID) -> EmpenhoOut:
    """Empenha um recurso numa ocorrência (RF-05).

    A defesa definitiva contra duplo empenho (OBJ-3) é o índice único parcial
    `uq_empenho_ativo_por_recurso` no banco — a checagem de `recurso.estado`
    abaixo só existe para devolver, no caminho feliz, um erro em português
    (RNF-05) sem precisar esperar o banco rejeitar.
    """
    recurso = db.get(Recurso, dados.recurso_id)
    if recurso is None:
        raise ErroNegocio(404, "Recurso não encontrado.")
    ocorrencia = db.get(Ocorrencia, dados.ocorrencia_id)
    if ocorrencia is None:
        raise ErroNegocio(404, "Ocorrência não encontrada.")
    if ocorrencia.status != StatusOcorrencia.aberta:
        raise ErroNegocio(409, "Ocorrência está encerrada; não é possível empenhar recursos nela.")
    if recurso.estado != EstadoRecurso.disponivel:
        raise ErroNegocio(
            409,
            f"Recurso '{recurso.nome}' está '{recurso.estado.value}', não 'disponível'. "
            "Só é possível empenhar recursos disponíveis; escolha outro recurso ou libere este primeiro.",
        )
    if dados.demanda_id is not None:
        demanda = db.get(Demanda, dados.demanda_id)
        if demanda is None or demanda.ocorrencia_id != ocorrencia.id:
            raise ErroNegocio(422, "A demanda informada não pertence a esta ocorrência.")

    empenho = Empenho(
        recurso_id=recurso.id,
        ocorrencia_id=ocorrencia.id,
        demanda_id=dados.demanda_id,
        autor_empenho_id=autor_id,
    )
    db.add(empenho)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        if "uq_empenho_ativo_por_recurso" in str(getattr(exc, "orig", exc)):
            raise ErroNegocio(
                409,
                f"Recurso '{recurso.nome}' acabou de ser empenhado em outra requisição. "
                "Atualize a lista de recursos disponíveis e escolha outro.",
            ) from exc
        raise

    recurso.estado = EstadoRecurso.empenhado
    db.commit()
    db.refresh(empenho)
    return _para_out(empenho, recurso_nome=recurso.nome)


def liberar_empenho(db: Session, empenho_id: uuid.UUID, autor_id: uuid.UUID) -> EmpenhoOut:
    empenho = db.get(Empenho, empenho_id)
    if empenho is None:
        raise ErroNegocio(404, "Empenho não encontrado.")
    if empenho.status != StatusEmpenho.ativo:
        raise ErroNegocio(409, "Este empenho já foi liberado anteriormente.")

    empenho.status = StatusEmpenho.liberado
    empenho.liberado_em = func.now()
    empenho.autor_liberacao_id = autor_id

    recurso = db.get(Recurso, empenho.recurso_id)
    if recurso is not None:
        recurso.estado = EstadoRecurso.disponivel

    db.commit()
    db.refresh(empenho)
    return _para_out(empenho, recurso_nome=recurso.nome if recurso else None)


def listar_empenhos_por_ocorrencia(db: Session, ocorrencia_id: uuid.UUID) -> list[EmpenhoOut]:
    stmt = (
        select(Empenho, Recurso.nome)
        .join(Recurso, Recurso.id == Empenho.recurso_id)
        .where(Empenho.ocorrencia_id == ocorrencia_id)
        .order_by(Empenho.empenhado_em.desc())
    )
    return [_para_out(empenho, recurso_nome=nome) for empenho, nome in db.execute(stmt).all()]

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.auditoria import Auditoria
from app.models.usuario import Usuario
from app.schemas.auditoria import AuditoriaOut


def listar_auditoria(
    db: Session,
    *,
    tabela: str | None = None,
    registro_id: uuid.UUID | None = None,
    usuario_id: uuid.UUID | None = None,
    limite: int = 200,
) -> list[AuditoriaOut]:
    stmt = select(Auditoria, Usuario.nome).outerjoin(Usuario, Usuario.id == Auditoria.usuario_id)
    if tabela is not None:
        stmt = stmt.where(Auditoria.tabela == tabela)
    if registro_id is not None:
        stmt = stmt.where(Auditoria.registro_id == registro_id)
    if usuario_id is not None:
        stmt = stmt.where(Auditoria.usuario_id == usuario_id)
    stmt = stmt.order_by(Auditoria.criado_em.desc()).limit(limite)

    linhas = db.execute(stmt).all()
    saida = []
    for registro, nome_usuario in linhas:
        item = AuditoriaOut.model_validate(registro)
        item.usuario_nome = nome_usuario
        saida.append(item)
    return saida

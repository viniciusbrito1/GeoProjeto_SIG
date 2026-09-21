import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencias import exigir_coordenador
from app.database import get_db
from app.schemas.auditoria import AuditoriaOut
from app.services import auditoria as servico

router = APIRouter(prefix="/api/auditoria", tags=["auditoria"], dependencies=[Depends(exigir_coordenador)])


@router.get("", response_model=list[AuditoriaOut])
def listar(
    tabela: str | None = None,
    registro_id: uuid.UUID | None = None,
    usuario_id: uuid.UUID | None = None,
    limite: int = Query(default=200, le=1000),
    db: Session = Depends(get_db),
) -> list[AuditoriaOut]:
    return servico.listar_auditoria(db, tabela=tabela, registro_id=registro_id, usuario_id=usuario_id, limite=limite)

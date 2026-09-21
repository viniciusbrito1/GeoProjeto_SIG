import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencias import exigir_operador_ou_coordenador, obter_usuario_atual, usuario_id_uuid
from app.database import get_db
from app.schemas.auth import UsuarioAutenticado
from app.schemas.empenho import EmpenhoCreate, EmpenhoOut
from app.services import empenhos as servico

router = APIRouter(prefix="/api/empenhos", tags=["empenhos"], dependencies=[Depends(exigir_operador_ou_coordenador)])


@router.post("", response_model=EmpenhoOut, status_code=201)
def empenhar(
    dados: EmpenhoCreate,
    db: Session = Depends(get_db),
    usuario: UsuarioAutenticado = Depends(obter_usuario_atual),
) -> EmpenhoOut:
    return servico.empenhar_recurso(db, dados, autor_id=usuario_id_uuid(usuario))


@router.post("/{empenho_id}/liberar", response_model=EmpenhoOut)
def liberar(
    empenho_id: uuid.UUID,
    db: Session = Depends(get_db),
    usuario: UsuarioAutenticado = Depends(obter_usuario_atual),
) -> EmpenhoOut:
    return servico.liberar_empenho(db, empenho_id, autor_id=usuario_id_uuid(usuario))

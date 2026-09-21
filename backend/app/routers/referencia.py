import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencias import exigir_coordenador, exigir_qualquer_perfil
from app.database import get_db
from app.models.auditoria import CamadaExterna
from app.models.orgao import Municipio, Orgao
from app.schemas.referencia import CamadaExternaCreate, CamadaExternaOut, CamadaExternaUpdate, MunicipioOut, OrgaoOut
from app.services.erros import ErroNegocio

router = APIRouter(prefix="/api", tags=["referência"], dependencies=[Depends(exigir_qualquer_perfil)])


@router.get("/orgaos", response_model=list[OrgaoOut])
def listar_orgaos(db: Session = Depends(get_db)) -> list[Orgao]:
    return list(db.execute(select(Orgao).order_by(Orgao.sigla)).scalars().all())


@router.get("/municipios", response_model=list[MunicipioOut])
def listar_municipios(db: Session = Depends(get_db)) -> list[Municipio]:
    return list(db.execute(select(Municipio).order_by(Municipio.nome)).scalars().all())


@router.get("/camadas-externas", response_model=list[CamadaExternaOut])
def listar_camadas_externas(incluir_inativas: bool = False, db: Session = Depends(get_db)) -> list[CamadaExterna]:
    """RF-15: registro de camadas WMS externas que o mapa deve consumir.

    Por padrão só as ativas (as que o mapa oferece); `incluir_inativas=true`
    serve à tela de gestão de camadas externas.
    """
    stmt = select(CamadaExterna).order_by(CamadaExterna.nome)
    if not incluir_inativas:
        stmt = stmt.where(CamadaExterna.ativa.is_(True))
    return list(db.execute(stmt).scalars().all())


@router.post("/camadas-externas", response_model=CamadaExternaOut, status_code=201, dependencies=[Depends(exigir_coordenador)])
def criar_camada_externa(dados: CamadaExternaCreate, db: Session = Depends(get_db)) -> CamadaExterna:
    camada = CamadaExterna(**dados.model_dump())
    db.add(camada)
    db.commit()
    db.refresh(camada)
    return camada


@router.patch("/camadas-externas/{camada_id}", response_model=CamadaExternaOut, dependencies=[Depends(exigir_coordenador)])
def atualizar_camada_externa(camada_id: uuid.UUID, dados: CamadaExternaUpdate, db: Session = Depends(get_db)) -> CamadaExterna:
    """Altera ou ativa/inativa uma camada externa. Não há exclusão: inativar
    tira a camada do mapa e preserva o histórico na auditoria (RF-13)."""
    camada = db.get(CamadaExterna, camada_id)
    if camada is None:
        raise ErroNegocio(404, "Camada externa não encontrada. Atualize a lista e tente de novo.")
    for campo, valor in dados.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(camada, campo, valor)
    db.commit()
    db.refresh(camada)
    return camada

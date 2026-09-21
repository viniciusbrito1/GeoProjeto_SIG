import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencias import exigir_coordenador, exigir_operador_ou_coordenador, exigir_qualquer_perfil
from app.database import get_db
from app.models.enums import EstadoRecurso, TipoRecurso
from app.models.orgao import Orgao
from app.models.recurso import Recurso
from app.schemas.recurso import RecursoAlterarEstado, RecursoCreate, RecursoOut, RecursoUpdate
from app.services import recursos as servico
from app.services.geo import geometria_para_geojson

router = APIRouter(prefix="/api/recursos", tags=["recursos"], dependencies=[Depends(exigir_qualquer_perfil)])


@router.get("", response_model=list[RecursoOut])
def listar(
    tipo: TipoRecurso | None = None,
    estado: EstadoRecurso | None = None,
    orgao_id: uuid.UUID | None = None,
    especialidade: str | None = None,
    somente_ativos: bool = True,
    lat: float | None = Query(default=None, description="Latitude do centro de busca (graus, SIRGAS2000)"),
    lon: float | None = Query(default=None, description="Longitude do centro de busca (graus, SIRGAS2000)"),
    raio_m: float | None = Query(default=None, gt=0, description="Raio de busca em metros (RF-07)"),
    db: Session = Depends(get_db),
) -> list[RecursoOut]:
    return servico.listar_recursos(
        db,
        tipo=tipo,
        estado=estado,
        orgao_id=orgao_id,
        especialidade=especialidade,
        somente_ativos=somente_ativos,
        lat=lat,
        lon=lon,
        raio_m=raio_m,
    )


@router.get("/geojson")
def listar_geojson(
    somente_ativos: bool = True,
    db: Session = Depends(get_db),
) -> dict:
    """Camada de recursos para o mapa (RF-08/RF-09/RF-10): tipo e estado em cada
    feature permitem simbolizar por forma (tipo) e cor (estado) no cliente."""
    stmt = select(Recurso, Orgao.sigla).join(Orgao, Orgao.id == Recurso.orgao_id)
    if somente_ativos:
        stmt = stmt.where(Recurso.ativo.is_(True))
    linhas = db.execute(stmt).all()
    features = [
        {
            "type": "Feature",
            "geometry": geometria_para_geojson(recurso.geom),
            "properties": {
                "id": str(recurso.id),
                "nome": recurso.nome,
                "tipo": recurso.tipo.value,
                "estado": recurso.estado.value,
                "orgao": sigla,
                "especialidade": recurso.especialidade,
            },
        }
        for recurso, sigla in linhas
    ]
    return {"type": "FeatureCollection", "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::4674"}}, "features": features}


@router.get("/compativeis/{demanda_id}", response_model=list[RecursoOut])
def compativeis(demanda_id: uuid.UUID, db: Session = Depends(get_db)) -> list[RecursoOut]:
    return servico.listar_recursos_compativeis_com_demanda(db, demanda_id)


@router.get("/{recurso_id}", response_model=RecursoOut)
def obter(recurso_id: uuid.UUID, db: Session = Depends(get_db)) -> RecursoOut:
    return servico.obter_recurso_out(db, recurso_id)


@router.post("", response_model=RecursoOut, status_code=201, dependencies=[Depends(exigir_coordenador)])
def criar(dados: RecursoCreate, db: Session = Depends(get_db)) -> RecursoOut:
    return servico.criar_recurso(db, dados)


@router.put("/{recurso_id}", response_model=RecursoOut, dependencies=[Depends(exigir_coordenador)])
def atualizar(recurso_id: uuid.UUID, dados: RecursoUpdate, db: Session = Depends(get_db)) -> RecursoOut:
    return servico.atualizar_recurso(db, recurso_id, dados)


@router.patch("/{recurso_id}/estado", response_model=RecursoOut, dependencies=[Depends(exigir_operador_ou_coordenador)])
def alterar_estado(recurso_id: uuid.UUID, dados: RecursoAlterarEstado, db: Session = Depends(get_db)) -> RecursoOut:
    return servico.alterar_estado_recurso(db, recurso_id, dados.estado)


@router.delete("/{recurso_id}", response_model=RecursoOut, dependencies=[Depends(exigir_coordenador)])
def inativar(recurso_id: uuid.UUID, db: Session = Depends(get_db)) -> RecursoOut:
    return servico.inativar_recurso(db, recurso_id)

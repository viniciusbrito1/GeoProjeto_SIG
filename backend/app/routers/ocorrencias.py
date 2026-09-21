import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencias import exigir_operador_ou_coordenador, exigir_qualquer_perfil, obter_usuario_atual, usuario_id_uuid
from app.database import get_db
from app.models.enums import StatusOcorrencia
from app.models.ocorrencia import Ocorrencia
from app.schemas.auth import UsuarioAutenticado
from app.schemas.empenho import EmpenhoOut
from app.schemas.ocorrencia import DemandaCreate, OcorrenciaCreate, OcorrenciaOut
from app.services import empenhos as servico_empenhos
from app.services import ocorrencias as servico
from app.services.geo import geometria_para_geojson

router = APIRouter(prefix="/api/ocorrencias", tags=["ocorrências"], dependencies=[Depends(exigir_qualquer_perfil)])


@router.get("", response_model=list[OcorrenciaOut])
def listar(status_filtro: StatusOcorrencia | None = None, db: Session = Depends(get_db)) -> list[OcorrenciaOut]:
    return servico.listar_ocorrencias(db, status_filtro=status_filtro)


@router.get("/geojson")
def listar_geojson(db: Session = Depends(get_db)) -> dict:
    """Camada de áreas atingidas para o mapa (RF-08)."""
    ocorrencias = db.execute(select(Ocorrencia)).scalars().all()
    features = [
        {
            "type": "Feature",
            "geometry": geometria_para_geojson(o.area_atingida),
            "properties": {
                "id": str(o.id),
                "tipo": o.tipo,
                "severidade": o.severidade.value,
                "status": o.status.value,
                "municipio_codigo_ibge": o.municipio_codigo_ibge,
            },
        }
        for o in ocorrencias
    ]
    return {"type": "FeatureCollection", "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::4674"}}, "features": features}


@router.get("/{ocorrencia_id}", response_model=OcorrenciaOut)
def obter(ocorrencia_id: uuid.UUID, db: Session = Depends(get_db)) -> OcorrenciaOut:
    return servico.obter_ocorrencia_out(db, ocorrencia_id)


@router.get("/{ocorrencia_id}/empenhos", response_model=list[EmpenhoOut])
def listar_empenhos(ocorrencia_id: uuid.UUID, db: Session = Depends(get_db)) -> list[EmpenhoOut]:
    return servico_empenhos.listar_empenhos_por_ocorrencia(db, ocorrencia_id)


@router.post("", response_model=OcorrenciaOut, status_code=201, dependencies=[Depends(exigir_operador_ou_coordenador)])
def criar(
    dados: OcorrenciaCreate,
    db: Session = Depends(get_db),
    usuario: UsuarioAutenticado = Depends(obter_usuario_atual),
) -> OcorrenciaOut:
    return servico.criar_ocorrencia(db, dados, criado_por=usuario_id_uuid(usuario))


@router.post(
    "/{ocorrencia_id}/demandas", response_model=OcorrenciaOut, status_code=201, dependencies=[Depends(exigir_operador_ou_coordenador)]
)
def adicionar_demanda(ocorrencia_id: uuid.UUID, dados: DemandaCreate, db: Session = Depends(get_db)) -> OcorrenciaOut:
    return servico.adicionar_demanda(db, ocorrencia_id, dados)


@router.post("/{ocorrencia_id}/encerrar", response_model=OcorrenciaOut, dependencies=[Depends(exigir_operador_ou_coordenador)])
def encerrar(ocorrencia_id: uuid.UUID, db: Session = Depends(get_db)) -> OcorrenciaOut:
    return servico.encerrar_ocorrencia(db, ocorrencia_id)

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import SeveridadeOcorrencia, StatusOcorrencia, TipoRecurso
from app.schemas.geo import GeoJSONMultiPolygon, GeoJSONPolygon


class DemandaCreate(BaseModel):
    tipo_recurso: TipoRecurso
    especialidade: str | None = None
    quantidade_necessaria: int = Field(gt=0)


class DemandaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ocorrencia_id: uuid.UUID
    tipo_recurso: TipoRecurso
    especialidade: str | None
    quantidade_necessaria: int
    quantidade_empenhada: int = 0
    saldo_descoberto: int = 0


class OcorrenciaCreate(BaseModel):
    tipo: str = Field(min_length=2, max_length=80)
    severidade: SeveridadeOcorrencia
    municipio_codigo_ibge: str = Field(min_length=7, max_length=7)
    area_atingida: GeoJSONPolygon | GeoJSONMultiPolygon
    descricao: str | None = None
    demandas: list[DemandaCreate] = []


class OcorrenciaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tipo: str
    severidade: SeveridadeOcorrencia
    municipio_codigo_ibge: str
    municipio_nome: str | None = None
    area_atingida: GeoJSONMultiPolygon
    descricao: str | None
    status: StatusOcorrencia
    criado_por: uuid.UUID
    criado_em: datetime
    encerrado_em: datetime | None
    demandas: list[DemandaOut] = []

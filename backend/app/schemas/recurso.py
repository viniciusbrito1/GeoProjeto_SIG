import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import EstadoRecurso, TipoRecurso
from app.schemas.geo import GeoJSONPoint


class RecursoBase(BaseModel):
    tipo: TipoRecurso
    nome: str = Field(min_length=2, max_length=160)
    orgao_id: uuid.UUID
    especialidade: str | None = None
    capacidade_valor: float | None = None
    capacidade_unidade: str | None = None
    localizacao: GeoJSONPoint


class RecursoCreate(RecursoBase):
    pass


class RecursoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=160)
    orgao_id: uuid.UUID | None = None
    especialidade: str | None = None
    capacidade_valor: float | None = None
    capacidade_unidade: str | None = None
    localizacao: GeoJSONPoint | None = None


class RecursoAlterarEstado(BaseModel):
    estado: EstadoRecurso


class RecursoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tipo: TipoRecurso
    nome: str
    orgao_id: uuid.UUID
    orgao_sigla: str | None = None
    especialidade: str | None
    capacidade_valor: float | None
    capacidade_unidade: str | None
    localizacao: GeoJSONPoint
    estado: EstadoRecurso
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
    distancia_m: float | None = None

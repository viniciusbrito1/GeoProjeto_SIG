import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import StatusEmpenho


class EmpenhoCreate(BaseModel):
    recurso_id: uuid.UUID
    ocorrencia_id: uuid.UUID
    demanda_id: uuid.UUID | None = None


class EmpenhoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    recurso_id: uuid.UUID
    recurso_nome: str | None = None
    ocorrencia_id: uuid.UUID
    demanda_id: uuid.UUID | None
    status: StatusEmpenho
    autor_empenho_id: uuid.UUID
    empenhado_em: datetime
    autor_liberacao_id: uuid.UUID | None
    liberado_em: datetime | None

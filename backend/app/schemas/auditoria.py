import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditoriaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tabela: str
    operacao: str
    registro_id: uuid.UUID | None
    usuario_id: uuid.UUID | None
    usuario_nome: str | None = None
    dados_antes: dict | None
    dados_depois: dict | None
    criado_em: datetime

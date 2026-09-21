import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Auditoria(Base):
    """Somente leitura pela aplicação: as linhas são gravadas por trigger de banco
    (ver migração 0001) e o papel de conexão da API não tem GRANT de INSERT/UPDATE/
    DELETE nesta tabela — isso é o que torna a trilha "não editável pela aplicação"
    (RF-13) uma garantia estrutural, não uma convenção de código.
    """

    __tablename__ = "auditoria"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    tabela: Mapped[str] = mapped_column(String(60), nullable=False)
    operacao: Mapped[str] = mapped_column(String(10), nullable=False)
    registro_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    dados_antes: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    dados_depois: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CamadaExterna(Base):
    __tablename__ = "camadas_externas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(160), nullable=False)
    url_wms: Mapped[str] = mapped_column(String(500), nullable=False)
    nome_camada: Mapped[str] = mapped_column(String(160), nullable=False)
    ativa: Mapped[bool] = mapped_column(default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

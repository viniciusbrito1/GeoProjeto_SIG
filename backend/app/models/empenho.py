import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import StatusEmpenho


class Empenho(Base):
    # OBJ-3 é garantido pelo índice único parcial `uq_empenho_ativo_por_recurso`
    # (recurso_id) WHERE status='ativo', criado na migração 0001 — não redeclarado
    # aqui (o schema é gerenciado só pelo Alembic, não por Base.metadata.create_all).
    __tablename__ = "empenhos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recurso_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("recursos.id"), nullable=False)
    ocorrencia_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ocorrencias.id"), nullable=False)
    demanda_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("demandas.id"), nullable=True)
    status: Mapped[StatusEmpenho] = mapped_column(
        Enum(StatusEmpenho, name="status_empenho", native_enum=True), nullable=False, default=StatusEmpenho.ativo
    )
    autor_empenho_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    empenhado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    autor_liberacao_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    liberado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

import uuid
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.config import get_settings
from app.database import Base
from app.models.enums import EstadoRecurso, TipoRecurso

SRID = get_settings().srid_armazenamento


class Recurso(Base):
    __tablename__ = "recursos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tipo: Mapped[TipoRecurso] = mapped_column(Enum(TipoRecurso, name="tipo_recurso", native_enum=True), nullable=False)
    nome: Mapped[str] = mapped_column(String(160), nullable=False)
    orgao_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orgaos.id"), nullable=False)
    especialidade: Mapped[str | None] = mapped_column(String(120), nullable=True)
    capacidade_valor: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    capacidade_unidade: Mapped[str | None] = mapped_column(String(40), nullable=True)
    geom: Mapped[str] = mapped_column(Geometry(geometry_type="POINT", srid=SRID), nullable=False)
    estado: Mapped[EstadoRecurso] = mapped_column(
        Enum(EstadoRecurso, name="estado_recurso", native_enum=True), nullable=False, default=EstadoRecurso.disponivel
    )
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

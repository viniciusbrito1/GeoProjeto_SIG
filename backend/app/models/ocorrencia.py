import uuid
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.config import get_settings
from app.database import Base
from app.models.enums import SeveridadeOcorrencia, StatusOcorrencia, TipoRecurso

SRID = get_settings().srid_armazenamento


class Ocorrencia(Base):
    __tablename__ = "ocorrencias"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tipo: Mapped[str] = mapped_column(String(80), nullable=False)
    severidade: Mapped[SeveridadeOcorrencia] = mapped_column(
        Enum(SeveridadeOcorrencia, name="severidade_ocorrencia", native_enum=True), nullable=False
    )
    municipio_codigo_ibge: Mapped[str] = mapped_column(String(7), ForeignKey("municipios.codigo_ibge"), nullable=False)
    area_atingida: Mapped[str] = mapped_column(Geometry(geometry_type="MULTIPOLYGON", srid=SRID), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[StatusOcorrencia] = mapped_column(
        Enum(StatusOcorrencia, name="status_ocorrencia", native_enum=True), nullable=False, default=StatusOcorrencia.aberta
    )
    criado_por: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    encerrado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Demanda(Base):
    __tablename__ = "demandas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ocorrencia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ocorrencias.id", ondelete="CASCADE"), nullable=False
    )
    tipo_recurso: Mapped[TipoRecurso] = mapped_column(Enum(TipoRecurso, name="tipo_recurso", native_enum=True), nullable=False)
    especialidade: Mapped[str | None] = mapped_column(String(120), nullable=True)
    quantidade_necessaria: Mapped[int] = mapped_column(Integer, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

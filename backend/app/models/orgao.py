import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Orgao(Base):
    __tablename__ = "orgaos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(160), nullable=False)
    sigla: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)


class Municipio(Base):
    __tablename__ = "municipios"

    codigo_ibge: Mapped[str] = mapped_column(String(7), primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    uf: Mapped[str] = mapped_column(String(2), nullable=False)

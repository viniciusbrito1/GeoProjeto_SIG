from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def set_db_usuario_atual(db: Session, usuario_id: str | None) -> None:
    """Expõe o usuário autenticado para os triggers de auditoria via variável de sessão do Postgres.

    A auditoria (RF-13) é gravada por trigger no banco, fora do alcance da aplicação;
    este é o único canal pelo qual o trigger sabe "quem" fez a escrita.
    """
    db.execute(
        text("SELECT set_config('app.current_user_id', :uid, true)"),
        {"uid": str(usuario_id) if usuario_id else ""},
    )

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker

from app.auth.seguranca import criar_access_token, gerar_hash_senha
from app.database import engine, get_db
from app.main import app
from app.models.enums import PerfilUsuario, SeveridadeOcorrencia
from app.models.ocorrencia import Ocorrencia
from app.models.orgao import Municipio, Orgao
from app.models.usuario import Usuario
from app.services.geo import geojson_para_geometria

# Cada teste roda dentro de uma transação externa com SAVEPOINT e sofre
# ROLLBACK no final — os triggers e constraints reais do Postgres continuam
# valendo (é justamente isso que queremos exercitar), mas nenhum teste
# enxerga dado de outro nem deixa lixo no banco. O serviço chama db.commit()
# normalmente; sem o listener abaixo, esse commit encerraria o SAVEPOINT e o
# teste deixaria de estar isolado — é o recipe padrão do SQLAlchemy para
# "joining a session into an external transaction" em suítes de teste.


@pytest.fixture()
def db_session():
    connection = engine.connect()
    transacao_externa = connection.begin()
    Sessao = sessionmaker(bind=connection)
    sessao = Sessao()
    sessao.begin_nested()

    @event.listens_for(sessao, "after_transaction_end")
    def _reabrir_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()

    yield sessao

    sessao.close()
    transacao_externa.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    def _get_db_override():
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def orgao(db_session):
    org = Orgao(id=uuid.uuid4(), nome="Defesa Civil de Teste", sigla=f"DCT-{uuid.uuid4().hex[:6]}")
    db_session.add(org)
    db_session.commit()
    return org


@pytest.fixture()
def municipio(db_session):
    mun = db_session.get(Municipio, "3205309")
    if mun is None:
        mun = Municipio(codigo_ibge="3205309", nome="Vitória", uf="ES")
        db_session.add(mun)
        db_session.commit()
    return mun


def _criar_usuario(db_session, perfil: PerfilUsuario) -> Usuario:
    usuario = Usuario(
        id=uuid.uuid4(),
        nome=f"Usuário {perfil.value}",
        email=f"{perfil.value}-{uuid.uuid4().hex[:6]}@teste.local",
        senha_hash=gerar_hash_senha("senha-teste-123"),
        perfil=perfil,
    )
    db_session.add(usuario)
    db_session.commit()
    return usuario


@pytest.fixture()
def usuario_coordenador(db_session):
    return _criar_usuario(db_session, PerfilUsuario.coordenador)


@pytest.fixture()
def usuario_operador(db_session):
    return _criar_usuario(db_session, PerfilUsuario.operador)


@pytest.fixture()
def usuario_consulta(db_session):
    return _criar_usuario(db_session, PerfilUsuario.consulta)


@pytest.fixture()
def ocorrencia_aberta(db_session, municipio, usuario_coordenador):
    poligono = {
        "type": "MultiPolygon",
        "coordinates": [[[(-40.35, -20.35), (-40.25, -20.35), (-40.25, -20.25), (-40.35, -20.25), (-40.35, -20.35)]]],
    }
    ocorrencia = Ocorrencia(
        id=uuid.uuid4(),
        tipo="Alagamento",
        severidade=SeveridadeOcorrencia.alta,
        municipio_codigo_ibge=municipio.codigo_ibge,
        area_atingida=geojson_para_geometria(poligono),
        criado_por=usuario_coordenador.id,
    )
    db_session.add(ocorrencia)
    db_session.commit()
    return {"id": str(ocorrencia.id)}


def token_para(usuario: Usuario) -> str:
    return criar_access_token(sub=str(usuario.id), perfil=usuario.perfil.value, nome=usuario.nome, email=usuario.email)


def cabecalho_auth(usuario: Usuario) -> dict:
    return {"Authorization": f"Bearer {token_para(usuario)}"}

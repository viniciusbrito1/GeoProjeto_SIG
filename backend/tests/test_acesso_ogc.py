"""Regras de acesso às camadas OGC (RNF-09, RF-11).

O nginx consulta `GET /api/auth/verificar-ogc` antes de repassar qualquer
requisição a /geoserver/*: 204 libera, 401 bloqueia. Testamos a decisão aqui;
o encaixe com o nginx é verificado manualmente (ver matriz de rastreabilidade).
"""

import base64

from tests.conftest import cabecalho_auth, token_para

URL = "/api/auth/verificar-ogc"


def _basic(email: str, senha: str) -> dict:
    return {"Authorization": "Basic " + base64.b64encode(f"{email}:{senha}".encode()).decode()}


def test_sem_credencial_e_bloqueado(client):
    assert client.get(URL).status_code == 401


def test_bearer_valido_libera(client, usuario_consulta):
    assert client.get(URL, headers=cabecalho_auth(usuario_consulta)).status_code == 204


def test_bearer_invalido_e_bloqueado(client):
    assert client.get(URL, headers={"Authorization": "Bearer token-falso"}).status_code == 401


def test_cookie_de_sessao_do_mapa_libera(client, usuario_operador):
    """Tiles WMS do navegador não mandam Authorization; usam o cookie gravado por /sessao-ogc."""
    resposta = client.post("/api/auth/sessao-ogc", headers=cabecalho_auth(usuario_operador))
    assert resposta.status_code == 204
    set_cookie = resposta.headers["set-cookie"]
    assert "siscoord_ogc=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "Path=/geoserver" in set_cookie

    cookie = {"Cookie": f"siscoord_ogc={token_para(usuario_operador)}"}
    assert client.get(URL, headers=cookie).status_code == 204


def test_sessao_ogc_exige_login(client):
    assert client.post("/api/auth/sessao-ogc").status_code == 401


def test_logout_remove_cookie_de_sessao_ogc(client):
    resposta = client.post("/api/auth/logout")
    assert resposta.status_code == 204
    assert 'siscoord_ogc=""' in resposta.headers["set-cookie"] or "Max-Age=0" in resposta.headers["set-cookie"]


def test_basic_com_senha_correta_libera_cliente_sig(client, usuario_consulta):
    """RF-11: QGIS e afins autenticam com e-mail e senha de um usuário ativo."""
    assert client.get(URL, headers=_basic(usuario_consulta.email, "senha-teste-123")).status_code == 204


def test_basic_com_senha_errada_e_bloqueado(client, usuario_consulta):
    assert client.get(URL, headers=_basic(usuario_consulta.email, "senha-errada")).status_code == 401


def test_usuario_inativo_perde_acesso_ogc(client, db_session, usuario_coordenador):
    credenciais = _basic(usuario_coordenador.email, "senha-teste-123")
    assert client.get(URL, headers=credenciais).status_code == 204

    usuario_coordenador.ativo = False
    db_session.commit()

    assert client.get(URL, headers=credenciais).status_code == 401
    assert client.get(URL, headers=cabecalho_auth(usuario_coordenador)).status_code == 401

"""Controle de acesso às camadas OGC (WMS/WFS) do GeoServer.

O GeoServer não conhece os usuários do SISCOORD-DC, então quem decide se uma
requisição a `/geoserver/*` pode passar é a API: o nginx faz um `auth_request`
para `GET /api/auth/verificar-ogc` antes de repassar ao GeoServer (ver
`nginx/nginx.conf`). Isso atende às regras de acesso da IDE-Defesa (RNF-09)
sem duplicar cadastro de usuários no GeoServer.

Três formas de credencial são aceitas, porque há dois tipos de cliente:

- **navegador (frontend):** os tiles do Leaflet são `<img>` e não conseguem
  enviar o cabeçalho `Authorization`; por isso, após o login, a API grava o
  mesmo JWT num cookie `HttpOnly` restrito ao caminho `/geoserver`;
- **cliente SIG desktop (QGIS, ArcGIS etc.) — RF-11:** HTTP Basic com o
  e-mail e a senha de um usuário ativo do sistema;
- **scripts e integrações:** `Authorization: Bearer <JWT>`.
"""

import base64
import hashlib
import time
import uuid

import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.seguranca import decodificar_access_token, verificar_senha
from app.models.usuario import Usuario

COOKIE_SESSAO_OGC = "siscoord_ogc"
CAMINHO_COOKIE_OGC = "/geoserver"

# Um cliente SIG manda as mesmas credenciais Basic em toda requisição (um mapa
# pode disparar dezenas). Verificar bcrypt em cada uma custaria ~100 ms por
# requisição; guardamos por pouco tempo só o hash das credenciais já
# validadas. O usuário continua sendo relido do banco a cada vez, então
# inativá-lo corta o acesso imediatamente.
_TTL_CACHE_BASIC_S = 300
_MAX_CACHE_BASIC = 1000
_cache_basic: dict[str, tuple[uuid.UUID, float]] = {}


def _usuario_ativo(db: Session, usuario_id: uuid.UUID) -> Usuario | None:
    usuario = db.get(Usuario, usuario_id)
    return usuario if usuario is not None and usuario.ativo else None


def _usuario_por_jwt(db: Session, token: str) -> Usuario | None:
    try:
        payload = decodificar_access_token(token)
        return _usuario_ativo(db, uuid.UUID(payload["sub"]))
    except (jwt.PyJWTError, KeyError, ValueError):
        return None


def _usuario_por_basic(db: Session, credenciais_b64: str) -> Usuario | None:
    chave_cache = hashlib.sha256(credenciais_b64.encode()).hexdigest()
    agora = time.monotonic()
    em_cache = _cache_basic.get(chave_cache)
    if em_cache is not None and em_cache[1] > agora:
        return _usuario_ativo(db, em_cache[0])

    try:
        email, _, senha = base64.b64decode(credenciais_b64).decode("utf-8").partition(":")
    except (ValueError, UnicodeDecodeError):
        return None

    usuario = db.execute(select(Usuario).where(Usuario.email == email)).scalar_one_or_none()
    if usuario is None or not usuario.ativo or not verificar_senha(senha, usuario.senha_hash):
        return None

    if len(_cache_basic) >= _MAX_CACHE_BASIC:
        _cache_basic.clear()
    _cache_basic[chave_cache] = (usuario.id, agora + _TTL_CACHE_BASIC_S)
    return usuario


def usuario_da_requisicao_ogc(db: Session, authorization: str | None, cookie_sessao: str | None) -> Usuario | None:
    """Devolve o usuário ativo dono da credencial, ou None se não houver credencial válida."""
    if authorization:
        esquema, _, valor = authorization.partition(" ")
        if esquema.lower() == "bearer" and valor:
            return _usuario_por_jwt(db, valor.strip())
        if esquema.lower() == "basic" and valor:
            return _usuario_por_basic(db, valor.strip())
        return None
    if cookie_sessao:
        return _usuario_por_jwt(db, cookie_sessao)
    return None

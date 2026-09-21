from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.acesso_ogc import CAMINHO_COOKIE_OGC, COOKIE_SESSAO_OGC, usuario_da_requisicao_ogc
from app.auth.dependencias import oauth2_scheme, obter_usuario_atual
from app.auth.seguranca import criar_access_token, verificar_senha
from app.config import get_settings
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, TokenResponse, UsuarioAutenticado

router = APIRouter(prefix="/api/auth", tags=["autenticação"])
settings = get_settings()


@router.post("/login", response_model=TokenResponse)
def login(dados: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    usuario = db.execute(select(Usuario).where(Usuario.email == dados.email)).scalar_one_or_none()
    if usuario is None or not usuario.ativo or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")

    token = criar_access_token(sub=str(usuario.id), perfil=usuario.perfil.value, nome=usuario.nome, email=usuario.email)
    return TokenResponse(access_token=token, perfil=usuario.perfil, nome=usuario.nome)


@router.get("/me", response_model=UsuarioAutenticado)
def me(usuario: UsuarioAutenticado = Depends(obter_usuario_atual)) -> UsuarioAutenticado:
    return usuario


@router.post("/sessao-ogc", status_code=204)
def abrir_sessao_ogc(
    response: Response,
    token: str | None = Depends(oauth2_scheme),
    _usuario: UsuarioAutenticado = Depends(obter_usuario_atual),
) -> Response:
    """Grava o JWT num cookie HttpOnly restrito a /geoserver, para que os tiles
    WMS pedidos pelo mapa (tags <img>, sem cabeçalho Authorization) passem pelo
    controle de acesso do proxy (RNF-09). O frontend chama após login e ao
    restaurar a sessão."""
    response.status_code = 204
    response.set_cookie(
        COOKIE_SESSAO_OGC,
        token or "",
        max_age=settings.jwt_expira_minutos * 60,
        path=CAMINHO_COOKIE_OGC,
        httponly=True,
        secure=True,
        samesite="strict",
    )
    return response


@router.post("/logout", status_code=204)
def logout(response: Response) -> Response:
    """Encerra a sessão OGC do navegador. O JWT da API é descartado pelo próprio frontend."""
    response.status_code = 204
    response.delete_cookie(COOKIE_SESSAO_OGC, path=CAMINHO_COOKIE_OGC, httponly=True, secure=True, samesite="strict")
    return response


@router.get("/verificar-ogc", status_code=204, include_in_schema=False)
def verificar_acesso_ogc(
    response: Response,
    authorization: str | None = Header(default=None),
    cookie_sessao: str | None = Cookie(default=None, alias=COOKIE_SESSAO_OGC),
    db: Session = Depends(get_db),
) -> Response:
    """Chamado pelo nginx (`auth_request`) antes de cada requisição a /geoserver/*.

    Qualquer perfil (Coordenador, Operador ou Consulta) pode ler as camadas; o
    que se exige é um usuário autenticado e ativo. 204 libera, 401 bloqueia.
    """
    if usuario_da_requisicao_ogc(db, authorization, cookie_sessao) is None:
        raise HTTPException(status_code=401, detail="Autenticação necessária para acessar as camadas OGC.")
    response.status_code = 204
    return response

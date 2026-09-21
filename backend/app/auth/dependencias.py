import uuid
from collections.abc import Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.seguranca import decodificar_access_token
from app.database import get_db, set_db_usuario_atual
from app.models.enums import PerfilUsuario
from app.schemas.auth import UsuarioAutenticado

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def obter_usuario_atual(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UsuarioAutenticado:
    erro_credenciais = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sessão inválida ou expirada. Faça login novamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise erro_credenciais
    try:
        payload = decodificar_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Sessão expirada. Faça login novamente.") from None
    except jwt.PyJWTError:
        raise erro_credenciais from None

    usuario = UsuarioAutenticado(
        id=payload["sub"], nome=payload["nome"], email=payload["email"], perfil=PerfilUsuario(payload["perfil"])
    )
    # Torna o usuário visível ao trigger de auditoria (RF-13) para o resto da requisição.
    set_db_usuario_atual(db, usuario.id)
    return usuario


def exigir_perfil(*perfis_permitidos: PerfilUsuario) -> Callable:
    def dependencia(usuario: UsuarioAutenticado = Depends(obter_usuario_atual)) -> UsuarioAutenticado:
        if usuario.perfil not in perfis_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Seu perfil ({usuario.perfil.value}) não tem permissão para esta ação.",
            )
        return usuario

    return dependencia


# Atalhos de RBAC (RF-12): Coordenador tem escrita total; Operador tem escrita
# restrita às operações de campo (ocorrências, demandas, empenhos); cadastro
# mestre de recursos e gestão de usuários é só do Coordenador; Consulta é
# somente leitura em tudo (não usa estes atalhos de escrita).
exigir_coordenador = exigir_perfil(PerfilUsuario.coordenador)
exigir_operador_ou_coordenador = exigir_perfil(PerfilUsuario.operador, PerfilUsuario.coordenador)
exigir_qualquer_perfil = exigir_perfil(PerfilUsuario.coordenador, PerfilUsuario.operador, PerfilUsuario.consulta)


def usuario_id_uuid(usuario: UsuarioAutenticado) -> uuid.UUID:
    return uuid.UUID(usuario.id)

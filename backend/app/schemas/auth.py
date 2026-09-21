from pydantic import BaseModel, EmailStr

from app.models.enums import PerfilUsuario


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    perfil: PerfilUsuario
    nome: str


class UsuarioAutenticado(BaseModel):
    id: str
    nome: str
    email: str
    perfil: PerfilUsuario

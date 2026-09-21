import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencias import exigir_coordenador
from app.auth.seguranca import gerar_hash_senha
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioOut

router = APIRouter(prefix="/api/usuarios", tags=["usuários"], dependencies=[Depends(exigir_coordenador)])


@router.get("", response_model=list[UsuarioOut])
def listar(db: Session = Depends(get_db)) -> list[Usuario]:
    return list(db.execute(select(Usuario).order_by(Usuario.nome)).scalars().all())


@router.post("", response_model=UsuarioOut, status_code=201)
def criar(dados: UsuarioCreate, db: Session = Depends(get_db)) -> Usuario:
    if db.execute(select(Usuario).where(Usuario.email == dados.email)).scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Já existe um usuário cadastrado com este e-mail.")
    usuario = Usuario(nome=dados.nome, email=dados.email, senha_hash=gerar_hash_senha(dados.senha), perfil=dados.perfil)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.patch("/{usuario_id}/inativar", response_model=UsuarioOut)
def inativar(usuario_id: uuid.UUID, db: Session = Depends(get_db)) -> Usuario:
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    usuario.ativo = False
    db.commit()
    db.refresh(usuario)
    return usuario

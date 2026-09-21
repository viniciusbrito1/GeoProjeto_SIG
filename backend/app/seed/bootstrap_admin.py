"""Cria o primeiro usuário Coordenador, se ainda não existir nenhum.

Necessário porque criar usuários pela API exige já estar autenticado como
Coordenador (RF-12) — alguém precisa existir antes. Rodar uma vez após as
migrações: `python -m app.seed.bootstrap_admin` (o entrypoint do container
de backend já faz isso).
"""

import os
import sys

from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy import select

from app.auth.seguranca import gerar_hash_senha
from app.database import SessionLocal
from app.models.enums import PerfilUsuario
from app.models.usuario import Usuario


def executar() -> None:
    nome = os.environ.get("ADMIN_NOME", "Administrador")
    email = os.environ.get("ADMIN_EMAIL", "admin@siscoorddc.gov.br")
    senha = os.environ.get("ADMIN_SENHA", "troque-esta-senha-123")

    try:
        TypeAdapter(EmailStr).validate_python(email)
    except ValidationError as exc:
        # Esse script grava direto no banco, sem passar pela validação da API
        # (não dá pra logar sem existir usuário ainda) — só por isso, sem essa
        # checagem, um ADMIN_EMAIL inválido criaria uma conta com a qual
        # ninguém consegue logar (o login usa o mesmo EmailStr da API).
        print(f"ADMIN_EMAIL inválido ({email!r}): {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    db = SessionLocal()
    try:
        existe_coordenador = db.execute(select(Usuario).where(Usuario.perfil == PerfilUsuario.coordenador)).first()
        if existe_coordenador:
            print("Já existe ao menos um usuário Coordenador; nada a fazer.")
            return

        usuario = Usuario(nome=nome, email=email, senha_hash=gerar_hash_senha(senha), perfil=PerfilUsuario.coordenador)
        db.add(usuario)
        db.commit()
        print(f"Usuário Coordenador criado: {email} (defina ADMIN_SENHA no .env antes de ir para produção).")
    finally:
        db.close()


if __name__ == "__main__":
    executar()

"""schema inicial: extensoes, tipos, tabelas, indices espaciais, triggers de auditoria e estado, papel restrito da app

Revision ID: 0001
Revises:
Create Date: 2026-09-14

"""

import os
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.execute("CREATE TYPE perfil_usuario AS ENUM ('coordenador', 'operador', 'consulta')")
    op.execute("CREATE TYPE tipo_recurso AS ENUM ('equipe', 'instalacao', 'equipamento')")
    op.execute("CREATE TYPE estado_recurso AS ENUM ('disponivel', 'empenhado', 'indisponivel', 'inativo')")
    op.execute("CREATE TYPE severidade_ocorrencia AS ENUM ('baixa', 'media', 'alta', 'critica')")
    op.execute("CREATE TYPE status_ocorrencia AS ENUM ('aberta', 'encerrada')")
    op.execute("CREATE TYPE status_empenho AS ENUM ('ativo', 'liberado')")

    op.execute(
        """
        CREATE TABLE usuarios (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            nome VARCHAR(120) NOT NULL,
            email VARCHAR(160) NOT NULL UNIQUE,
            senha_hash VARCHAR(255) NOT NULL,
            perfil perfil_usuario NOT NULL DEFAULT 'consulta',
            ativo BOOLEAN NOT NULL DEFAULT TRUE,
            criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE orgaos (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            nome VARCHAR(160) NOT NULL,
            sigla VARCHAR(20) NOT NULL UNIQUE
        )
        """
    )

    op.execute(
        """
        CREATE TABLE municipios (
            codigo_ibge CHAR(7) PRIMARY KEY,
            nome VARCHAR(120) NOT NULL,
            uf CHAR(2) NOT NULL
        )
        """
    )

    op.execute(
        f"""
        CREATE TABLE recursos (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tipo tipo_recurso NOT NULL,
            nome VARCHAR(160) NOT NULL,
            orgao_id UUID NOT NULL REFERENCES orgaos(id),
            especialidade VARCHAR(120),
            capacidade_valor NUMERIC(12, 2),
            capacidade_unidade VARCHAR(40),
            geom geometry(Point, 4674) NOT NULL,
            estado estado_recurso NOT NULL DEFAULT 'disponivel',
            ativo BOOLEAN NOT NULL DEFAULT TRUE,
            criado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
            atualizado_em TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX idx_recursos_geom ON recursos USING GIST(geom)")
    op.execute("CREATE INDEX idx_recursos_tipo_estado ON recursos(tipo, estado)")
    op.execute("CREATE INDEX idx_recursos_orgao ON recursos(orgao_id)")

    op.execute(
        """
        CREATE TABLE ocorrencias (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tipo VARCHAR(80) NOT NULL,
            severidade severidade_ocorrencia NOT NULL,
            municipio_codigo_ibge CHAR(7) NOT NULL REFERENCES municipios(codigo_ibge),
            area_atingida geometry(MultiPolygon, 4674) NOT NULL,
            descricao TEXT,
            status status_ocorrencia NOT NULL DEFAULT 'aberta',
            criado_por UUID NOT NULL REFERENCES usuarios(id),
            criado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
            encerrado_em TIMESTAMPTZ
        )
        """
    )
    op.execute("CREATE INDEX idx_ocorrencias_geom ON ocorrencias USING GIST(area_atingida)")
    op.execute("CREATE INDEX idx_ocorrencias_status ON ocorrencias(status)")
    op.execute("CREATE INDEX idx_ocorrencias_municipio ON ocorrencias(municipio_codigo_ibge)")

    op.execute(
        """
        CREATE TABLE demandas (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            ocorrencia_id UUID NOT NULL REFERENCES ocorrencias(id) ON DELETE CASCADE,
            tipo_recurso tipo_recurso NOT NULL,
            especialidade VARCHAR(120),
            quantidade_necessaria INTEGER NOT NULL CHECK (quantidade_necessaria > 0),
            criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX idx_demandas_ocorrencia ON demandas(ocorrencia_id)")

    op.execute(
        """
        CREATE TABLE empenhos (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            recurso_id UUID NOT NULL REFERENCES recursos(id),
            ocorrencia_id UUID NOT NULL REFERENCES ocorrencias(id),
            demanda_id UUID REFERENCES demandas(id),
            status status_empenho NOT NULL DEFAULT 'ativo',
            autor_empenho_id UUID NOT NULL REFERENCES usuarios(id),
            empenhado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
            autor_liberacao_id UUID REFERENCES usuarios(id),
            liberado_em TIMESTAMPTZ
        )
        """
    )
    # Núcleo do OBJ-3: impede, no próprio banco, que um recurso tenha dois
    # empenhos ativos simultâneos — mesmo sob requisições concorrentes.
    op.execute("CREATE UNIQUE INDEX uq_empenho_ativo_por_recurso ON empenhos(recurso_id) WHERE status = 'ativo'")
    op.execute("CREATE INDEX idx_empenhos_ocorrencia ON empenhos(ocorrencia_id)")

    op.execute(
        """
        CREATE TABLE camadas_externas (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            nome VARCHAR(160) NOT NULL,
            url_wms VARCHAR(500) NOT NULL,
            nome_camada VARCHAR(160) NOT NULL,
            ativa BOOLEAN NOT NULL DEFAULT TRUE,
            criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE auditoria (
            id BIGSERIAL PRIMARY KEY,
            tabela VARCHAR(60) NOT NULL,
            operacao VARCHAR(10) NOT NULL,
            registro_id UUID,
            usuario_id UUID,
            dados_antes JSONB,
            dados_depois JSONB,
            criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX idx_auditoria_tabela_data ON auditoria(tabela, criado_em DESC)")
    op.execute("CREATE INDEX idx_auditoria_registro ON auditoria(registro_id)")

    # --- Trigger de validação de transição de estado (RF-02) ---------------
    op.execute(
        """
        CREATE OR REPLACE FUNCTION fn_recursos_valida_estado() RETURNS TRIGGER AS $$
        BEGIN
            IF OLD.estado = NEW.estado THEN
                RETURN NEW;
            END IF;

            IF (OLD.estado, NEW.estado) NOT IN (
                ('disponivel', 'empenhado'),
                ('disponivel', 'indisponivel'),
                ('disponivel', 'inativo'),
                ('empenhado', 'disponivel'),
                ('indisponivel', 'disponivel'),
                ('indisponivel', 'inativo'),
                ('inativo', 'disponivel')
            ) THEN
                RAISE EXCEPTION 'Transição de estado inválida: % -> % (recurso %)', OLD.estado, NEW.estado, OLD.id
                    USING ERRCODE = '23514';
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_recursos_valida_estado
            BEFORE UPDATE OF estado ON recursos
            FOR EACH ROW
            EXECUTE FUNCTION fn_recursos_valida_estado()
        """
    )

    # --- Trigger genérico de auditoria (RF-13) ------------------------------
    # SECURITY DEFINER: roda com os privilégios de quem é dono da função (o
    # papel de migração, dono do schema) e não do papel restrito da API — é
    # isso que permite gravar em `auditoria` mesmo sem a API ter GRANT de
    # escrita ali.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION fn_auditoria() RETURNS TRIGGER AS $$
        DECLARE
            v_usuario_id UUID;
        BEGIN
            BEGIN
                v_usuario_id := NULLIF(current_setting('app.current_user_id', true), '')::UUID;
            EXCEPTION WHEN OTHERS THEN
                v_usuario_id := NULL;
            END;

            IF TG_OP = 'INSERT' THEN
                INSERT INTO auditoria(tabela, operacao, registro_id, usuario_id, dados_antes, dados_depois)
                VALUES (TG_TABLE_NAME, TG_OP, NEW.id, v_usuario_id, NULL, to_jsonb(NEW));
                RETURN NEW;
            ELSIF TG_OP = 'UPDATE' THEN
                INSERT INTO auditoria(tabela, operacao, registro_id, usuario_id, dados_antes, dados_depois)
                VALUES (TG_TABLE_NAME, TG_OP, NEW.id, v_usuario_id, to_jsonb(OLD), to_jsonb(NEW));
                RETURN NEW;
            ELSIF TG_OP = 'DELETE' THEN
                INSERT INTO auditoria(tabela, operacao, registro_id, usuario_id, dados_antes, dados_depois)
                VALUES (TG_TABLE_NAME, TG_OP, OLD.id, v_usuario_id, to_jsonb(OLD), NULL);
                RETURN OLD;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER
        """
    )
    for tabela in ("recursos", "ocorrencias", "demandas", "empenhos", "usuarios"):
        op.execute(
            f"""
            CREATE TRIGGER trg_auditoria_{tabela}
                AFTER INSERT OR UPDATE OR DELETE ON {tabela}
                FOR EACH ROW
                EXECUTE FUNCTION fn_auditoria()
            """
        )

    # --- Papel restrito para a API (RNF-06 / RF-13) -------------------------
    # A senha vem de variável de ambiente lida no momento da migração — nunca
    # fica hardcoded no arquivo. Ver .env.example / docs/manual-instalacao.md.
    senha_app = os.environ.get("APP_DB_PASSWORD", "siscoord_app_troque_esta_senha").replace("'", "''")
    op.execute(
        f"""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'siscoord_app') THEN
                CREATE ROLE siscoord_app LOGIN PASSWORD '{senha_app}';
            ELSE
                ALTER ROLE siscoord_app PASSWORD '{senha_app}';
            END IF;
        END
        $$
        """
    )
    op.execute("GRANT USAGE ON SCHEMA public TO siscoord_app")
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE ON "
        "usuarios, orgaos, municipios, recursos, ocorrencias, demandas, empenhos, camadas_externas "
        "TO siscoord_app"
    )
    # Só leitura na auditoria: nenhum GRANT de escrita, só o trigger (SECURITY
    # DEFINER) consegue popular a tabela.
    op.execute("GRANT SELECT ON auditoria TO siscoord_app")
    op.execute("REVOKE INSERT, UPDATE, DELETE ON auditoria FROM siscoord_app")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS auditoria CASCADE")
    op.execute("DROP TABLE IF EXISTS camadas_externas CASCADE")
    op.execute("DROP TABLE IF EXISTS empenhos CASCADE")
    op.execute("DROP TABLE IF EXISTS demandas CASCADE")
    op.execute("DROP TABLE IF EXISTS ocorrencias CASCADE")
    op.execute("DROP TABLE IF EXISTS recursos CASCADE")
    op.execute("DROP TABLE IF EXISTS municipios CASCADE")
    op.execute("DROP TABLE IF EXISTS orgaos CASCADE")
    op.execute("DROP TABLE IF EXISTS usuarios CASCADE")
    op.execute("DROP FUNCTION IF EXISTS fn_auditoria CASCADE")
    op.execute("DROP FUNCTION IF EXISTS fn_recursos_valida_estado CASCADE")
    op.execute("DROP TYPE IF EXISTS status_empenho")
    op.execute("DROP TYPE IF EXISTS status_ocorrencia")
    op.execute("DROP TYPE IF EXISTS severidade_ocorrencia")
    op.execute("DROP TYPE IF EXISTS estado_recurso")
    op.execute("DROP TYPE IF EXISTS tipo_recurso")
    op.execute("DROP TYPE IF EXISTS perfil_usuario")

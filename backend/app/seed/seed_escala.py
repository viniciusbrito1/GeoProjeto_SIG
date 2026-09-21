"""Gera massa de dados para o teste de escala do RNF-10: >=500 recursos e
>=20 ocorrências, com alguns empenhos ativos. Coordenadas dos municípios são
aproximadas (centro da sede) — servem para demonstração/teste de carga, não
para uso operacional real.

Uso: python -m app.seed.seed_escala [--recursos 600] [--ocorrencias 25]
"""

import argparse
import random
import uuid

from sqlalchemy import select

from app.database import SessionLocal
from app.models.empenho import Empenho
from app.models.enums import EstadoRecurso, SeveridadeOcorrencia, StatusEmpenho, TipoRecurso
from app.models.ocorrencia import Demanda, Ocorrencia
from app.models.orgao import Municipio, Orgao
from app.models.recurso import Recurso
from app.models.usuario import Usuario
from app.services.geo import geojson_para_geometria

MUNICIPIOS_CENTRO = {
    "3205309": (-40.3128, -20.3155),  # Vitória (lon, lat)
    "3205200": (-40.2925, -20.3297),  # Vila Velha
    "3201308": (-40.4173, -20.2618),  # Cariacica
    "3205002": (-40.3078, -20.1289),  # Serra
    "3201209": (-41.1128, -20.8489),  # Cachoeiro de Itapemirim
    "3203205": (-40.0722, -19.3911),  # Linhares
    "3201506": (-40.6306, -19.5386),  # Colatina
    "3202405": (-40.4986, -20.6667),  # Guarapari
}

NOMES_EQUIPE = ["Equipe Resgate", "Equipe SAR", "Brigada", "Guarnição", "Equipe Médica Avançada"]
NOMES_INSTALACAO = ["Abrigo Temporário", "Posto de Triagem", "Base de Apoio", "Centro de Operações"]
NOMES_EQUIPAMENTO = ["Viatura de Resgate", "Bote Inflável", "Caminhão-Pipa", "Retroescavadeira", "Gerador Móvel", "Ambulância"]
ESPECIALIDADES = ["busca e salvamento", "atendimento médico", "logística", "engenharia", "transporte"]


def _ponto_proximo(lon: float, lat: float, raio_graus: float = 0.08) -> dict:
    return {
        "type": "Point",
        "coordinates": (lon + random.uniform(-raio_graus, raio_graus), lat + random.uniform(-raio_graus, raio_graus)),
    }


def _poligono_proximo(lon: float, lat: float, meio_lado_graus: float = 0.02) -> dict:
    cx = lon + random.uniform(-0.05, 0.05)
    cy = lat + random.uniform(-0.05, 0.05)
    anel = [
        (cx - meio_lado_graus, cy - meio_lado_graus),
        (cx + meio_lado_graus, cy - meio_lado_graus),
        (cx + meio_lado_graus, cy + meio_lado_graus),
        (cx - meio_lado_graus, cy + meio_lado_graus),
        (cx - meio_lado_graus, cy - meio_lado_graus),
    ]
    return {"type": "MultiPolygon", "coordinates": [[anel]]}


def gerar(n_recursos: int, n_ocorrencias: int) -> None:
    db = SessionLocal()
    try:
        orgaos = list(db.execute(select(Orgao)).scalars().all())
        municipios = list(db.execute(select(Municipio)).scalars().all())
        usuario = db.execute(select(Usuario)).scalars().first()
        if not orgaos or not municipios or usuario is None:
            raise SystemExit("Rode a seed de referência (sql/seed_referencia.sql) e o bootstrap_admin antes desta.")

        print(f"Gerando {n_recursos} recursos...")
        recursos = []
        for i in range(n_recursos):
            municipio = random.choice(municipios)
            lon, lat = MUNICIPIOS_CENTRO.get(municipio.codigo_ibge, (-40.5, -20.0))
            tipo = random.choices(
                [TipoRecurso.equipe, TipoRecurso.instalacao, TipoRecurso.equipamento], weights=[0.35, 0.15, 0.5]
            )[0]
            nome_base = {
                TipoRecurso.equipe: NOMES_EQUIPE,
                TipoRecurso.instalacao: NOMES_INSTALACAO,
                TipoRecurso.equipamento: NOMES_EQUIPAMENTO,
            }[tipo]
            estado = random.choices(
                [EstadoRecurso.disponivel, EstadoRecurso.indisponivel], weights=[0.85, 0.15]
            )[0]
            recursos.append(
                Recurso(
                    id=uuid.uuid4(),
                    tipo=tipo,
                    nome=f"{random.choice(nome_base)} {i + 1:03d}",
                    orgao_id=random.choice(orgaos).id,
                    especialidade=random.choice(ESPECIALIDADES),
                    capacidade_valor=random.choice([4, 8, 10, 20, 40, 100]),
                    capacidade_unidade=random.choice(["pessoas", "litros", "toneladas"]),
                    geom=geojson_para_geometria(_ponto_proximo(lon, lat)),
                    estado=estado,
                )
            )
            if len(recursos) >= 200:
                db.add_all(recursos)
                db.commit()
                recursos = []
        if recursos:
            db.add_all(recursos)
            db.commit()

        print(f"Gerando {n_ocorrencias} ocorrências com demandas...")
        ocorrencias = []
        for i in range(n_ocorrencias):
            municipio = random.choice(municipios)
            lon, lat = MUNICIPIOS_CENTRO.get(municipio.codigo_ibge, (-40.5, -20.0))
            ocorrencia = Ocorrencia(
                id=uuid.uuid4(),
                tipo=random.choice(["Alagamento", "Deslizamento", "Vendaval", "Rompimento de barragem", "Enchente"]),
                severidade=random.choice(list(SeveridadeOcorrencia)),
                municipio_codigo_ibge=municipio.codigo_ibge,
                area_atingida=geojson_para_geometria(_poligono_proximo(lon, lat)),
                descricao=f"Ocorrência de teste de escala #{i + 1} (RNF-10).",
                criado_por=usuario.id,
            )
            db.add(ocorrencia)
            db.flush()
            for _ in range(random.randint(1, 3)):
                db.add(
                    Demanda(
                        ocorrencia_id=ocorrencia.id,
                        tipo_recurso=random.choice(list(TipoRecurso)),
                        especialidade=random.choice(ESPECIALIDADES),
                        quantidade_necessaria=random.randint(1, 6),
                    )
                )
            ocorrencias.append(ocorrencia)
        db.commit()

        print("Empenhando alguns recursos disponíveis...")
        disponiveis = list(db.execute(select(Recurso).where(Recurso.estado == EstadoRecurso.disponivel)).scalars().all())
        random.shuffle(disponiveis)
        n_empenhos = min(len(disponiveis) // 4, 150)
        for recurso in disponiveis[:n_empenhos]:
            ocorrencia = random.choice(ocorrencias)
            db.add(
                Empenho(
                    recurso_id=recurso.id,
                    ocorrencia_id=ocorrencia.id,
                    autor_empenho_id=usuario.id,
                )
            )
            recurso.estado = EstadoRecurso.empenhado
        db.commit()

        print(f"Concluído: {n_recursos} recursos, {n_ocorrencias} ocorrências, {n_empenhos} empenhos ativos.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--recursos", type=int, default=600)
    parser.add_argument("--ocorrencias", type=int, default=25)
    args = parser.parse_args()
    gerar(args.recursos, args.ocorrencias)

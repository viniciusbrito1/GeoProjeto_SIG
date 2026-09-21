import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.empenho import Empenho
from app.models.enums import StatusEmpenho, StatusOcorrencia
from app.models.ocorrencia import Demanda, Ocorrencia
from app.models.orgao import Municipio
from app.schemas.ocorrencia import DemandaOut, OcorrenciaCreate, OcorrenciaOut
from app.services.erros import ErroNegocio
from app.services.geo import geojson_para_geometria, geometria_para_geojson, polygon_para_multipolygon


def _demanda_para_out(db: Session, demanda: Demanda) -> DemandaOut:
    empenhada = db.execute(
        select(func.count())
        .select_from(Empenho)
        .where(Empenho.demanda_id == demanda.id, Empenho.status == StatusEmpenho.ativo)
    ).scalar_one()
    return DemandaOut(
        id=demanda.id,
        ocorrencia_id=demanda.ocorrencia_id,
        tipo_recurso=demanda.tipo_recurso,
        especialidade=demanda.especialidade,
        quantidade_necessaria=demanda.quantidade_necessaria,
        quantidade_empenhada=empenhada,
        saldo_descoberto=max(0, demanda.quantidade_necessaria - empenhada),
    )


def _ocorrencia_para_out(db: Session, ocorrencia: Ocorrencia) -> OcorrenciaOut:
    municipio = db.get(Municipio, ocorrencia.municipio_codigo_ibge)
    demandas = db.execute(select(Demanda).where(Demanda.ocorrencia_id == ocorrencia.id)).scalars().all()
    return OcorrenciaOut(
        id=ocorrencia.id,
        tipo=ocorrencia.tipo,
        severidade=ocorrencia.severidade,
        municipio_codigo_ibge=ocorrencia.municipio_codigo_ibge,
        municipio_nome=municipio.nome if municipio else None,
        area_atingida=geometria_para_geojson(ocorrencia.area_atingida),
        descricao=ocorrencia.descricao,
        status=ocorrencia.status,
        criado_por=ocorrencia.criado_por,
        criado_em=ocorrencia.criado_em,
        encerrado_em=ocorrencia.encerrado_em,
        demandas=[_demanda_para_out(db, d) for d in demandas],
    )


def obter_ocorrencia(db: Session, ocorrencia_id: uuid.UUID) -> Ocorrencia:
    ocorrencia = db.get(Ocorrencia, ocorrencia_id)
    if ocorrencia is None:
        raise ErroNegocio(404, "Ocorrência não encontrada.")
    return ocorrencia


def criar_ocorrencia(db: Session, dados: OcorrenciaCreate, criado_por: uuid.UUID) -> OcorrenciaOut:
    if db.get(Municipio, dados.municipio_codigo_ibge) is None:
        raise ErroNegocio(422, "Código IBGE de município desconhecido. Cadastre o município antes da ocorrência.")

    geojson_multi = polygon_para_multipolygon(dados.area_atingida.model_dump())
    ocorrencia = Ocorrencia(
        tipo=dados.tipo,
        severidade=dados.severidade,
        municipio_codigo_ibge=dados.municipio_codigo_ibge,
        area_atingida=geojson_para_geometria(geojson_multi),
        descricao=dados.descricao,
        criado_por=criado_por,
    )
    db.add(ocorrencia)
    db.flush()

    for demanda_dados in dados.demandas:
        db.add(
            Demanda(
                ocorrencia_id=ocorrencia.id,
                tipo_recurso=demanda_dados.tipo_recurso,
                especialidade=demanda_dados.especialidade,
                quantidade_necessaria=demanda_dados.quantidade_necessaria,
            )
        )

    db.commit()
    db.refresh(ocorrencia)
    return _ocorrencia_para_out(db, ocorrencia)


def listar_ocorrencias(db: Session, *, status_filtro: StatusOcorrencia | None = None) -> list[OcorrenciaOut]:
    stmt = select(Ocorrencia).order_by(Ocorrencia.criado_em.desc())
    if status_filtro is not None:
        stmt = stmt.where(Ocorrencia.status == status_filtro)
    ocorrencias = db.execute(stmt).scalars().all()
    return [_ocorrencia_para_out(db, o) for o in ocorrencias]


def obter_ocorrencia_out(db: Session, ocorrencia_id: uuid.UUID) -> OcorrenciaOut:
    return _ocorrencia_para_out(db, obter_ocorrencia(db, ocorrencia_id))


def adicionar_demanda(db: Session, ocorrencia_id: uuid.UUID, dados) -> OcorrenciaOut:
    ocorrencia = obter_ocorrencia(db, ocorrencia_id)
    if ocorrencia.status != StatusOcorrencia.aberta:
        raise ErroNegocio(409, "Ocorrência está encerrada; não é possível registrar novas demandas.")
    db.add(
        Demanda(
            ocorrencia_id=ocorrencia.id,
            tipo_recurso=dados.tipo_recurso,
            especialidade=dados.especialidade,
            quantidade_necessaria=dados.quantidade_necessaria,
        )
    )
    db.commit()
    return _ocorrencia_para_out(db, ocorrencia)


def encerrar_ocorrencia(db: Session, ocorrencia_id: uuid.UUID) -> OcorrenciaOut:
    ocorrencia = obter_ocorrencia(db, ocorrencia_id)
    empenhos_ativos = db.execute(
        select(func.count())
        .select_from(Empenho)
        .where(Empenho.ocorrencia_id == ocorrencia_id, Empenho.status == StatusEmpenho.ativo)
    ).scalar_one()
    if empenhos_ativos > 0:
        raise ErroNegocio(
            409,
            f"Há {empenhos_ativos} recurso(s) ainda empenhado(s) nesta ocorrência. "
            "Libere todos os empenhos antes de encerrá-la.",
        )
    ocorrencia.status = StatusOcorrencia.encerrada
    ocorrencia.encerrado_em = func.now()
    db.commit()
    db.refresh(ocorrencia)
    return _ocorrencia_para_out(db, ocorrencia)

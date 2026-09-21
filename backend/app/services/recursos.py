import uuid

from geoalchemy2.types import Geography
from sqlalchemy import cast, func, select
from sqlalchemy.orm import Session

from app.models.enums import TRANSICOES_ESTADO_VALIDAS, EstadoRecurso, TipoRecurso
from app.models.ocorrencia import Demanda, Ocorrencia
from app.models.orgao import Orgao
from app.models.recurso import Recurso
from app.schemas.recurso import RecursoCreate, RecursoOut, RecursoUpdate
from app.services.erros import ErroNegocio
from app.services.geo import geojson_para_geometria, geometria_para_geojson


def _geography(expressao):
    """Converte uma expressão de geometria (armazenada em SIRGAS2000/4674) para
    `geography` a fim de calcular distância em metros com ST_Distance/ST_DWithin.

    O cast direto `::geography` do PostGIS só aceita SRID 4326 (WGS84) — tentar
    com 4674 falha em tempo de execução com "Geometry SRID (4674) does not
    match column SRID (4326)". SIRGAS2000 e WGS84 são geograficamente quase
    idênticos (diferença de poucos centímetros no Brasil), então o ST_Transform
    aqui é barato e não compromete a precisão da busca por raio (RF-07) nem do
    ordenamento por distância (RF-06). O dado permanece armazenado em 4674
    (RNF-02) — a transformação existe só para este cálculo.
    """
    return cast(func.ST_Transform(expressao, 4326), Geography)


def _para_out(recurso: Recurso, orgao_sigla: str | None = None, distancia_m: float | None = None) -> RecursoOut:
    return RecursoOut(
        id=recurso.id,
        tipo=recurso.tipo,
        nome=recurso.nome,
        orgao_id=recurso.orgao_id,
        orgao_sigla=orgao_sigla,
        especialidade=recurso.especialidade,
        capacidade_valor=float(recurso.capacidade_valor) if recurso.capacidade_valor is not None else None,
        capacidade_unidade=recurso.capacidade_unidade,
        localizacao=geometria_para_geojson(recurso.geom),
        estado=recurso.estado,
        ativo=recurso.ativo,
        criado_em=recurso.criado_em,
        atualizado_em=recurso.atualizado_em,
        distancia_m=round(distancia_m, 1) if distancia_m is not None else None,
    )


def obter_recurso(db: Session, recurso_id: uuid.UUID) -> Recurso:
    recurso = db.get(Recurso, recurso_id)
    if recurso is None:
        raise ErroNegocio(404, "Recurso não encontrado.")
    return recurso


def obter_recurso_out(db: Session, recurso_id: uuid.UUID) -> RecursoOut:
    recurso = obter_recurso(db, recurso_id)
    orgao = db.get(Orgao, recurso.orgao_id)
    return _para_out(recurso, orgao_sigla=orgao.sigla if orgao else None)


def criar_recurso(db: Session, dados: RecursoCreate) -> RecursoOut:
    if db.get(Orgao, dados.orgao_id) is None:
        raise ErroNegocio(422, "Órgão de origem informado não existe. Cadastre o órgão antes do recurso.")

    recurso = Recurso(
        tipo=dados.tipo,
        nome=dados.nome,
        orgao_id=dados.orgao_id,
        especialidade=dados.especialidade,
        capacidade_valor=dados.capacidade_valor,
        capacidade_unidade=dados.capacidade_unidade,
        geom=geojson_para_geometria(dados.localizacao.model_dump()),
    )
    db.add(recurso)
    db.commit()
    db.refresh(recurso)
    orgao = db.get(Orgao, recurso.orgao_id)
    return _para_out(recurso, orgao_sigla=orgao.sigla if orgao else None)


def atualizar_recurso(db: Session, recurso_id: uuid.UUID, dados: RecursoUpdate) -> RecursoOut:
    recurso = obter_recurso(db, recurso_id)
    campos = dados.model_dump(exclude_unset=True, exclude={"localizacao"})
    for campo, valor in campos.items():
        setattr(recurso, campo, valor)
    if dados.localizacao is not None:
        recurso.geom = geojson_para_geometria(dados.localizacao.model_dump())
    db.commit()
    db.refresh(recurso)
    orgao = db.get(Orgao, recurso.orgao_id)
    return _para_out(recurso, orgao_sigla=orgao.sigla if orgao else None)


def alterar_estado_recurso(db: Session, recurso_id: uuid.UUID, novo_estado: EstadoRecurso) -> RecursoOut:
    """Muda o estado operacional de um recurso "manualmente" (ex.: indisponível
    por manutenção). 'empenhado' fica de fora de propósito: essa transição só
    pode acontecer como efeito colateral de POST /api/empenhos (que cria o
    registro de empenho junto) — permiti-la aqui deixaria o recurso marcado
    como empenhado sem nenhum empenho correspondente, quebrando RF-05."""
    recurso = obter_recurso(db, recurso_id)
    if recurso.estado == EstadoRecurso.empenhado or novo_estado == EstadoRecurso.empenhado:
        raise ErroNegocio(
            409,
            "O estado 'empenhado' só muda via empenho/liberação (use POST /api/empenhos "
            "ou POST /api/empenhos/{id}/liberar), não por esta rota.",
        )
    permitidas = TRANSICOES_ESTADO_VALIDAS.get(recurso.estado, set())
    if novo_estado != recurso.estado and novo_estado not in permitidas:
        opcoes = ", ".join(e.value for e in permitidas) or "nenhuma — recurso em estado terminal"
        raise ErroNegocio(
            409,
            f"Não é possível mudar o recurso de '{recurso.estado.value}' para '{novo_estado.value}'. "
            f"A partir de '{recurso.estado.value}' você pode ir para: {opcoes}.",
        )
    recurso.estado = novo_estado
    db.commit()
    db.refresh(recurso)
    orgao = db.get(Orgao, recurso.orgao_id)
    return _para_out(recurso, orgao_sigla=orgao.sigla if orgao else None)


def inativar_recurso(db: Session, recurso_id: uuid.UUID) -> RecursoOut:
    recurso = obter_recurso(db, recurso_id)
    if recurso.estado == EstadoRecurso.empenhado:
        raise ErroNegocio(
            409,
            "Recurso está empenhado numa ocorrência. Libere o empenho antes de inativar o recurso.",
        )
    return alterar_estado_recurso(db, recurso_id, EstadoRecurso.inativo)


def listar_recursos(
    db: Session,
    *,
    tipo: TipoRecurso | None = None,
    estado: EstadoRecurso | None = None,
    orgao_id: uuid.UUID | None = None,
    especialidade: str | None = None,
    somente_ativos: bool = True,
    lat: float | None = None,
    lon: float | None = None,
    raio_m: float | None = None,
) -> list[RecursoOut]:
    ponto_busca = None
    distancia_col = None
    if lat is not None and lon is not None:
        ponto_busca = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4674)
        distancia_col = func.ST_Distance(_geography(Recurso.geom), _geography(ponto_busca)).label("distancia_m")

    colunas = [Recurso, Orgao.sigla] + ([distancia_col] if distancia_col is not None else [])
    stmt = select(*colunas).join(Orgao, Orgao.id == Recurso.orgao_id)

    if somente_ativos:
        stmt = stmt.where(Recurso.ativo.is_(True))
    if tipo is not None:
        stmt = stmt.where(Recurso.tipo == tipo)
    if estado is not None:
        stmt = stmt.where(Recurso.estado == estado)
    if orgao_id is not None:
        stmt = stmt.where(Recurso.orgao_id == orgao_id)
    if especialidade:
        stmt = stmt.where(Recurso.especialidade.ilike(f"%{especialidade}%"))
    if ponto_busca is not None and raio_m is not None:
        stmt = stmt.where(func.ST_DWithin(_geography(Recurso.geom), _geography(ponto_busca), raio_m))

    stmt = stmt.order_by(distancia_col if distancia_col is not None else Recurso.nome)

    linhas = db.execute(stmt).all()
    saida = []
    for linha in linhas:
        recurso, sigla = linha[0], linha[1]
        dist = linha[2] if len(linha) > 2 else None
        saida.append(_para_out(recurso, orgao_sigla=sigla, distancia_m=dist))
    return saida


def listar_recursos_compativeis_com_demanda(db: Session, demanda_id: uuid.UUID) -> list[RecursoOut]:
    """RF-06: recursos disponíveis e compatíveis com uma demanda, ordenados pela
    distância até a área atingida da ocorrência (centróide, em metros)."""
    demanda = db.get(Demanda, demanda_id)
    if demanda is None:
        raise ErroNegocio(404, "Demanda não encontrada.")

    centro_ocorrencia = (
        select(func.ST_Centroid(Ocorrencia.area_atingida)).where(Ocorrencia.id == demanda.ocorrencia_id).scalar_subquery()
    )
    distancia_col = func.ST_Distance(_geography(Recurso.geom), _geography(centro_ocorrencia)).label("distancia_m")

    stmt = (
        select(Recurso, Orgao.sigla, distancia_col)
        .join(Orgao, Orgao.id == Recurso.orgao_id)
        .where(Recurso.ativo.is_(True), Recurso.estado == EstadoRecurso.disponivel, Recurso.tipo == demanda.tipo_recurso)
    )
    if demanda.especialidade:
        stmt = stmt.where(Recurso.especialidade == demanda.especialidade)
    stmt = stmt.order_by(distancia_col)

    linhas = db.execute(stmt).all()
    return [_para_out(recurso, orgao_sigla=sigla, distancia_m=dist) for recurso, sigla, dist in linhas]

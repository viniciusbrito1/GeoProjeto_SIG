import io
import uuid
from datetime import datetime, timezone

from geoalchemy2.shape import to_shape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.empenho import Empenho
from app.models.enums import StatusEmpenho
from app.models.ocorrencia import Ocorrencia
from app.models.orgao import Municipio, Orgao
from app.models.recurso import Recurso
from app.models.usuario import Usuario
from app.services.erros import ErroNegocio
from app.services.ocorrencias import obter_ocorrencia, obter_ocorrencia_out

settings = get_settings()


def _dados_sitrep(db: Session, ocorrencia_id: uuid.UUID) -> dict:
    ocorrencia = obter_ocorrencia(db, ocorrencia_id)
    municipio = db.get(Municipio, ocorrencia.municipio_codigo_ibge)
    criador = db.get(Usuario, ocorrencia.criado_por)

    empenhos_stmt = (
        select(Empenho, Recurso, Orgao.sigla, Usuario.nome)
        .join(Recurso, Recurso.id == Empenho.recurso_id)
        .join(Orgao, Orgao.id == Recurso.orgao_id)
        .join(Usuario, Usuario.id == Empenho.autor_empenho_id)
        .where(Empenho.ocorrencia_id == ocorrencia_id, Empenho.status == StatusEmpenho.ativo)
        .order_by(Empenho.empenhado_em)
    )
    empenhos = db.execute(empenhos_stmt).all()

    return {
        "ocorrencia": ocorrencia,
        "municipio": municipio,
        "criador": criador,
        "empenhos": empenhos,
        "demandas": obter_ocorrencia_out(db, ocorrencia_id).demandas,
    }


def gerar_sitrep_pdf(db: Session, ocorrencia_id: uuid.UUID) -> bytes:
    dados = _dados_sitrep(db, ocorrencia_id)
    ocorrencia: Ocorrencia = dados["ocorrencia"]
    municipio = dados["municipio"]

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    estilos = getSampleStyleSheet()
    titulo = ParagraphStyle("titulo", parent=estilos["Title"], fontSize=16)
    subtitulo = ParagraphStyle("subtitulo", parent=estilos["Normal"], fontSize=10, textColor=colors.grey)

    elementos = [
        Paragraph("SITREP — Relatório de Situação", titulo),
        Paragraph("SISCOORD-DC · Sistema de Coordenação Geoespacial de Recursos de Defesa Civil", subtitulo),
        Spacer(1, 0.6 * cm),
        Paragraph(f"<b>Ocorrência:</b> {ocorrencia.tipo}", estilos["Normal"]),
        Paragraph(f"<b>Município:</b> {municipio.nome}/{municipio.uf} (IBGE {municipio.codigo_ibge})", estilos["Normal"]),
        Paragraph(f"<b>Severidade:</b> {ocorrencia.severidade.value}", estilos["Normal"]),
        Paragraph(f"<b>Status:</b> {ocorrencia.status.value}", estilos["Normal"]),
        Paragraph(f"<b>Aberta em:</b> {ocorrencia.criado_em.strftime('%d/%m/%Y %H:%M')} UTC", estilos["Normal"]),
        Paragraph(f"<b>Descrição:</b> {ocorrencia.descricao or '—'}", estilos["Normal"]),
        Paragraph(
            "<b>Sistema de referência da geometria:</b> SIRGAS 2000 / EPSG:4674",
            estilos["Normal"],
        ),
        Spacer(1, 0.6 * cm),
        Paragraph("Demandas e cobertura", estilos["Heading2"]),
    ]

    tabela_demandas = [["Tipo de recurso", "Especialidade", "Necessário", "Empenhado", "Saldo descoberto"]]
    for demanda in dados["demandas"]:
        tabela_demandas.append(
            [
                demanda.tipo_recurso.value,
                demanda.especialidade or "—",
                str(demanda.quantidade_necessaria),
                str(demanda.quantidade_empenhada),
                str(demanda.saldo_descoberto),
            ]
        )
    t1 = Table(tabela_demandas, colWidths=[4 * cm, 4 * cm, 2.5 * cm, 2.5 * cm, 3.5 * cm])
    t1.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3d5c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
            ]
        )
    )
    elementos += [t1, Spacer(1, 0.6 * cm), Paragraph("Recursos empenhados", estilos["Heading2"])]

    tabela_recursos = [["Recurso", "Tipo", "Órgão", "Empenhado por", "Data/hora"]]
    for empenho, recurso, sigla_orgao, nome_autor in dados["empenhos"]:
        tabela_recursos.append(
            [
                recurso.nome,
                recurso.tipo.value,
                sigla_orgao,
                nome_autor,
                empenho.empenhado_em.strftime("%d/%m/%Y %H:%M"),
            ]
        )
    if len(tabela_recursos) == 1:
        tabela_recursos.append(["Nenhum recurso empenhado no momento.", "", "", "", ""])
    t2 = Table(tabela_recursos, colWidths=[4 * cm, 2.5 * cm, 2.5 * cm, 4 * cm, 3.5 * cm])
    t2.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3d5c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
            ]
        )
    )
    elementos.append(t2)
    elementos.append(Spacer(1, 0.8 * cm))
    elementos.append(
        Paragraph(
            f"Gerado em {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M UTC')} pelo SISCOORD-DC.",
            subtitulo,
        )
    )

    doc.build(elementos)
    return buffer.getvalue()


def exportar_ocorrencia_geojson(db: Session, ocorrencia_id: uuid.UUID) -> dict:
    """RF-14 + RNF-03: exporta a ocorrência em formato vetorial aberto (GeoJSON),
    declarando explicitamente o SRC de origem (RNF-02)."""
    dados = _dados_sitrep(db, ocorrencia_id)
    ocorrencia: Ocorrencia = dados["ocorrencia"]

    area_geom = to_shape(ocorrencia.area_atingida)
    features = [
        {
            "type": "Feature",
            "geometry": area_geom.__geo_interface__,
            "properties": {
                "camada": "area_atingida",
                "ocorrencia_id": str(ocorrencia.id),
                "tipo": ocorrencia.tipo,
                "severidade": ocorrencia.severidade.value,
                "status": ocorrencia.status.value,
            },
        }
    ]
    for empenho, recurso, sigla_orgao, _nome_autor in dados["empenhos"]:
        ponto_geom = to_shape(recurso.geom)
        features.append(
            {
                "type": "Feature",
                "geometry": ponto_geom.__geo_interface__,
                "properties": {
                    "camada": "recurso_empenhado",
                    "recurso_id": str(recurso.id),
                    "nome": recurso.nome,
                    "tipo": recurso.tipo.value,
                    "orgao": sigla_orgao,
                    "empenhado_em": empenho.empenhado_em.isoformat(),
                },
            }
        )

    return {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": f"urn:ogc:def:crs:EPSG::{settings.srid_armazenamento}"}},
        "features": features,
    }


def exportar_ocorrencia_geopackage(db: Session, ocorrencia_id: uuid.UUID) -> bytes:
    """Grava duas camadas no mesmo .gpkg (área atingida e recursos empenhados)
    em vez de uma camada só com geometria mista — GeoPackage/QGIS lidam melhor
    com um tipo de geometria por camada, e RF-14 pede "as camadas" (plural)."""
    import tempfile
    from pathlib import Path

    import geopandas as gpd
    from shapely.geometry import shape as shapely_shape

    geojson = exportar_ocorrencia_geojson(db, ocorrencia_id)
    if not geojson["features"]:
        raise ErroNegocio(404, "Nada para exportar: ocorrência sem geometria de área.")

    crs = f"EPSG:{settings.srid_armazenamento}"
    por_camada: dict[str, list[dict]] = {}
    for feature in geojson["features"]:
        por_camada.setdefault(feature["properties"]["camada"], []).append(feature)

    with tempfile.TemporaryDirectory() as tmp:
        caminho = Path(tmp) / f"ocorrencia_{ocorrencia_id}.gpkg"
        for indice, (nome_camada, features) in enumerate(por_camada.items()):
            gdf = gpd.GeoDataFrame(
                [f["properties"] for f in features],
                geometry=[shapely_shape(f["geometry"]) for f in features],
                crs=crs,
            )
            gdf.to_file(caminho, layer=nome_camada, driver="GPKG", mode="w" if indice == 0 else "a")
        return caminho.read_bytes()

import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from app.auth.dependencias import exigir_qualquer_perfil
from app.database import get_db
from app.services import relatorios as servico

router = APIRouter(prefix="/api/ocorrencias", tags=["relatórios"], dependencies=[Depends(exigir_qualquer_perfil)])


@router.get("/{ocorrencia_id}/sitrep.pdf")
def sitrep_pdf(ocorrencia_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    """RF-14: relatório de situação (SITREP) por ocorrência, em PDF."""
    pdf_bytes = servico.gerar_sitrep_pdf(db, ocorrencia_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="sitrep_{ocorrencia_id}.pdf"'},
    )


@router.get("/{ocorrencia_id}/exportar")
def exportar(
    ocorrencia_id: uuid.UUID,
    formato: str = Query(default="geojson", pattern="^(geojson|gpkg)$"),
    db: Session = Depends(get_db),
) -> Response:
    """RF-14 + RNF-03: exporta as camadas da ocorrência em formato vetorial aberto."""
    if formato == "gpkg":
        conteudo = servico.exportar_ocorrencia_geopackage(db, ocorrencia_id)
        return Response(
            content=conteudo,
            media_type="application/geopackage+sqlite3",
            headers={"Content-Disposition": f'attachment; filename="ocorrencia_{ocorrencia_id}.gpkg"'},
        )
    geojson = servico.exportar_ocorrencia_geojson(db, ocorrencia_id)
    return JSONResponse(
        content=geojson,
        headers={"Content-Disposition": f'attachment; filename="ocorrencia_{ocorrencia_id}.geojson"'},
    )

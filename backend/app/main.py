from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import auditoria, auth, empenhos, ocorrencias, recursos, referencia, relatorios, usuarios

settings = get_settings()

# Documentação interativa sob /api/ para ficar acessível pelo proxy com TLS
# (https://<host>/api/docs) — a porta 8000 da API só é publicada no loopback
# do host (RNF-06).
app = FastAPI(
    title="SISCOORD-DC",
    description="Sistema de Coordenação Geoespacial de Recursos de Defesa Civil",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(referencia.router)
app.include_router(recursos.router)
app.include_router(ocorrencias.router)
app.include_router(empenhos.router)
app.include_router(auditoria.router)
app.include_router(relatorios.router)


@app.get("/api/health", tags=["infra"])
def health() -> dict:
    return {"status": "ok", "srid": settings.srid_armazenamento}

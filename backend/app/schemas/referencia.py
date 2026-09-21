import uuid

from pydantic import BaseModel, ConfigDict, field_validator


class OrgaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    sigla: str


class MunicipioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    codigo_ibge: str
    nome: str
    uf: str


def _validar_url_wms(valor: str) -> str:
    valor = valor.strip()
    if not valor.lower().startswith(("http://", "https://")):
        raise ValueError(
            "a URL do serviço WMS precisa começar com http:// ou https:// "
            "(ex.: https://geoservicos.ibge.gov.br/geoserver/wms)"
        )
    return valor


def _validar_texto_obrigatorio(valor: str) -> str:
    valor = valor.strip()
    if not valor:
        raise ValueError("campo obrigatório")
    return valor


class CamadaExternaCreate(BaseModel):
    nome: str
    url_wms: str
    nome_camada: str
    ativa: bool = True

    @field_validator("url_wms")
    @classmethod
    def _url(cls, valor: str) -> str:
        return _validar_url_wms(valor)

    @field_validator("nome", "nome_camada")
    @classmethod
    def _textos(cls, valor: str) -> str:
        return _validar_texto_obrigatorio(valor)


class CamadaExternaUpdate(BaseModel):
    nome: str | None = None
    url_wms: str | None = None
    nome_camada: str | None = None
    ativa: bool | None = None

    @field_validator("url_wms")
    @classmethod
    def _url(cls, valor: str | None) -> str | None:
        return None if valor is None else _validar_url_wms(valor)

    @field_validator("nome", "nome_camada")
    @classmethod
    def _textos(cls, valor: str | None) -> str | None:
        return None if valor is None else _validar_texto_obrigatorio(valor)


class CamadaExternaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    url_wms: str
    nome_camada: str
    ativa: bool

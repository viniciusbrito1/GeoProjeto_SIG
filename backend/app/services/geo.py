from typing import Any

from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping, shape

from app.config import get_settings

SRID = get_settings().srid_armazenamento


def geojson_para_geometria(geojson: dict[str, Any]) -> WKTElement:
    return WKTElement(shape(geojson).wkt, srid=SRID)


def geometria_para_geojson(geom_coluna) -> dict[str, Any] | None:
    if geom_coluna is None:
        return None
    return mapping(to_shape(geom_coluna))


def polygon_para_multipolygon(geojson: dict[str, Any]) -> dict[str, Any]:
    if geojson["type"] == "MultiPolygon":
        return geojson
    return {"type": "MultiPolygon", "coordinates": [geojson["coordinates"]]}

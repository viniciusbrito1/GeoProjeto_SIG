from typing import Literal

from pydantic import BaseModel


class GeoJSONPoint(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: tuple[float, float]  # [lon, lat], sempre SIRGAS 2000 / EPSG:4674 (RNF-02)


class GeoJSONPolygon(BaseModel):
    type: Literal["Polygon"] = "Polygon"
    coordinates: list[list[tuple[float, float]]]


class GeoJSONMultiPolygon(BaseModel):
    type: Literal["MultiPolygon"] = "MultiPolygon"
    coordinates: list[list[list[tuple[float, float]]]]

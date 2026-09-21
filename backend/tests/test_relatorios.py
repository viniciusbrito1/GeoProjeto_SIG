from tests.conftest import cabecalho_auth

POLIGONO_TESTE = {
    "type": "Polygon",
    "coordinates": [[[-40.35, -20.35], [-40.25, -20.35], [-40.25, -20.25], [-40.35, -20.25], [-40.35, -20.35]]],
}


def _criar_ocorrencia_com_empenho(client, orgao, municipio, usuario_coordenador, usuario_operador):
    headers_op = cabecalho_auth(usuario_operador)
    ocorrencia = client.post(
        "/api/ocorrencias",
        json={
            "tipo": "Enchente",
            "severidade": "alta",
            "municipio_codigo_ibge": municipio.codigo_ibge,
            "area_atingida": POLIGONO_TESTE,
            "demandas": [{"tipo_recurso": "equipe", "quantidade_necessaria": 2}],
        },
        headers=headers_op,
    ).json()
    recurso = client.post(
        "/api/recursos",
        json={
            "tipo": "equipe",
            "nome": "Equipe SITREP",
            "orgao_id": str(orgao.id),
            "localizacao": {"type": "Point", "coordinates": [-40.3, -20.3]},
        },
        headers=cabecalho_auth(usuario_coordenador),
    ).json()
    client.post(
        "/api/empenhos",
        json={"recurso_id": recurso["id"], "ocorrencia_id": ocorrencia["id"], "demanda_id": ocorrencia["demandas"][0]["id"]},
        headers=headers_op,
    )
    return ocorrencia


def test_sitrep_pdf_gerado_com_sucesso(client, orgao, municipio, usuario_coordenador, usuario_operador):
    ocorrencia = _criar_ocorrencia_com_empenho(client, orgao, municipio, usuario_coordenador, usuario_operador)

    resposta = client.get(f"/api/ocorrencias/{ocorrencia['id']}/sitrep.pdf", headers=cabecalho_auth(usuario_coordenador))
    assert resposta.status_code == 200
    assert resposta.headers["content-type"] == "application/pdf"
    assert resposta.content[:4] == b"%PDF"  # RF-14: relatório de situação


def test_exportar_geojson_declara_src(client, orgao, municipio, usuario_coordenador, usuario_operador):
    ocorrencia = _criar_ocorrencia_com_empenho(client, orgao, municipio, usuario_coordenador, usuario_operador)

    resposta = client.get(
        f"/api/ocorrencias/{ocorrencia['id']}/exportar", params={"formato": "geojson"}, headers=cabecalho_auth(usuario_coordenador)
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["type"] == "FeatureCollection"
    assert "4674" in corpo["crs"]["properties"]["name"]  # RNF-02: SRC explícito
    camadas = {f["properties"]["camada"] for f in corpo["features"]}
    assert "area_atingida" in camadas
    assert "recurso_empenhado" in camadas


def test_exportar_geopackage(client, orgao, municipio, usuario_coordenador, usuario_operador):
    ocorrencia = _criar_ocorrencia_com_empenho(client, orgao, municipio, usuario_coordenador, usuario_operador)

    resposta = client.get(
        f"/api/ocorrencias/{ocorrencia['id']}/exportar", params={"formato": "gpkg"}, headers=cabecalho_auth(usuario_coordenador)
    )
    assert resposta.status_code == 200
    assert resposta.headers["content-type"] == "application/geopackage+sqlite3"
    assert resposta.content[:16].startswith(b"SQLite format 3")  # GeoPackage = SQLite (RNF-03: formato aberto)

from tests.conftest import cabecalho_auth

POLIGONO_TESTE = {
    "type": "Polygon",
    "coordinates": [[[-40.35, -20.35], [-40.25, -20.35], [-40.25, -20.25], [-40.35, -20.25], [-40.35, -20.35]]],
}


def test_criar_ocorrencia_com_demandas(client, municipio, usuario_operador):
    payload = {
        "tipo": "Alagamento",
        "severidade": "alta",
        "municipio_codigo_ibge": municipio.codigo_ibge,
        "area_atingida": POLIGONO_TESTE,
        "descricao": "Teste RF-03/RF-04",
        "demandas": [
            {"tipo_recurso": "equipe", "especialidade": "resgate", "quantidade_necessaria": 3},
            {"tipo_recurso": "equipamento", "quantidade_necessaria": 2},
        ],
    }
    resposta = client.post("/api/ocorrencias", json=payload, headers=cabecalho_auth(usuario_operador))
    assert resposta.status_code == 201, resposta.text
    corpo = resposta.json()

    assert corpo["area_atingida"]["type"] == "MultiPolygon"  # Polygon vira MultiPolygon (RF-03 + schema)
    assert len(corpo["demandas"]) == 2
    for demanda in corpo["demandas"]:
        assert demanda["quantidade_empenhada"] == 0
        assert demanda["saldo_descoberto"] == demanda["quantidade_necessaria"]  # RF-04: nada empenhado ainda


def test_saldo_descoberto_diminui_ao_empenhar(client, orgao, municipio, usuario_coordenador, usuario_operador):
    headers_op = cabecalho_auth(usuario_operador)
    ocorrencia = client.post(
        "/api/ocorrencias",
        json={
            "tipo": "Deslizamento",
            "severidade": "critica",
            "municipio_codigo_ibge": municipio.codigo_ibge,
            "area_atingida": POLIGONO_TESTE,
            "demandas": [{"tipo_recurso": "equipe", "quantidade_necessaria": 1}],
        },
        headers=headers_op,
    ).json()
    demanda_id = ocorrencia["demandas"][0]["id"]

    recurso = client.post(
        "/api/recursos",
        json={
            "tipo": "equipe",
            "nome": "Equipe RF-06",
            "orgao_id": str(orgao.id),
            "localizacao": {"type": "Point", "coordinates": [-40.3, -20.3]},
        },
        headers=cabecalho_auth(usuario_coordenador),
    ).json()

    compativeis = client.get(f"/api/recursos/compativeis/{demanda_id}", headers=headers_op)
    assert compativeis.status_code == 200
    assert any(r["id"] == recurso["id"] for r in compativeis.json())  # RF-06

    client.post(
        "/api/empenhos",
        json={"recurso_id": recurso["id"], "ocorrencia_id": ocorrencia["id"], "demanda_id": demanda_id},
        headers=headers_op,
    )

    atualizada = client.get(f"/api/ocorrencias/{ocorrencia['id']}", headers=headers_op).json()
    demanda_atualizada = atualizada["demandas"][0]
    assert demanda_atualizada["quantidade_empenhada"] == 1
    assert demanda_atualizada["saldo_descoberto"] == 0


def test_busca_por_raio_e_atributos(client, orgao, usuario_coordenador):
    headers = cabecalho_auth(usuario_coordenador)
    client.post(
        "/api/recursos",
        json={
            "tipo": "equipamento",
            "nome": "Caminhão-Pipa RF-07",
            "orgao_id": str(orgao.id),
            "localizacao": {"type": "Point", "coordinates": [-40.30, -20.30]},
        },
        headers=headers,
    )

    perto = client.get("/api/recursos", params={"lat": -20.30, "lon": -40.30, "raio_m": 5000}, headers=headers)
    assert perto.status_code == 200
    assert any(r["nome"] == "Caminhão-Pipa RF-07" for r in perto.json())
    assert perto.json()[0]["distancia_m"] is not None

    longe = client.get("/api/recursos", params={"lat": -22.90, "lon": -43.20, "raio_m": 1000}, headers=headers)  # Rio de Janeiro
    assert longe.status_code == 200
    assert not any(r["nome"] == "Caminhão-Pipa RF-07" for r in longe.json())


def test_encerrar_ocorrencia_com_empenho_ativo_e_bloqueado(client, orgao, municipio, usuario_coordenador, usuario_operador):
    headers_op = cabecalho_auth(usuario_operador)
    ocorrencia = client.post(
        "/api/ocorrencias",
        json={
            "tipo": "Vendaval",
            "severidade": "media",
            "municipio_codigo_ibge": municipio.codigo_ibge,
            "area_atingida": POLIGONO_TESTE,
        },
        headers=headers_op,
    ).json()
    recurso = client.post(
        "/api/recursos",
        json={
            "tipo": "equipamento",
            "nome": "Gerador RF-Encerrar",
            "orgao_id": str(orgao.id),
            "localizacao": {"type": "Point", "coordinates": [-40.3, -20.3]},
        },
        headers=cabecalho_auth(usuario_coordenador),
    ).json()
    client.post("/api/empenhos", json={"recurso_id": recurso["id"], "ocorrencia_id": ocorrencia["id"]}, headers=headers_op)

    resposta = client.post(f"/api/ocorrencias/{ocorrencia['id']}/encerrar", headers=headers_op)
    assert resposta.status_code == 409

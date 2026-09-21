from tests.conftest import cabecalho_auth

CAMADA = {
    "nome": "Hidrografia de teste",
    "url_wms": "https://geoservicos.ibge.gov.br/geoserver/wms",
    "nome_camada": "CCAR:Hidrografia_2016",
}


def test_coordenador_cadastra_e_inativa_camada_externa(client, usuario_coordenador):
    """RF-15: a camada cadastrada aparece para o mapa; inativada, some do mapa mas continua listável na gestão."""
    headers = cabecalho_auth(usuario_coordenador)
    criada = client.post("/api/camadas-externas", json=CAMADA, headers=headers)
    assert criada.status_code == 201
    camada_id = criada.json()["id"]

    ativas = client.get("/api/camadas-externas", headers=headers).json()
    assert camada_id in [c["id"] for c in ativas]

    inativada = client.patch(f"/api/camadas-externas/{camada_id}", json={"ativa": False}, headers=headers)
    assert inativada.status_code == 200
    assert inativada.json()["ativa"] is False

    ativas = client.get("/api/camadas-externas", headers=headers).json()
    assert camada_id not in [c["id"] for c in ativas]
    todas = client.get("/api/camadas-externas", params={"incluir_inativas": True}, headers=headers).json()
    assert camada_id in [c["id"] for c in todas]


def test_url_wms_invalida_e_rejeitada_com_mensagem_em_portugues(client, usuario_coordenador):
    resposta = client.post(
        "/api/camadas-externas", json={**CAMADA, "url_wms": "geoservicos.ibge.gov.br/wms"}, headers=cabecalho_auth(usuario_coordenador)
    )
    assert resposta.status_code == 422
    assert "http://" in str(resposta.json()["detail"])


def test_operador_e_consulta_nao_gerenciam_camadas_externas(client, usuario_operador, usuario_consulta):
    """RF-12: gestão de camadas externas é só do Coordenador; os demais perfis só leem."""
    for usuario in (usuario_operador, usuario_consulta):
        headers = cabecalho_auth(usuario)
        assert client.post("/api/camadas-externas", json=CAMADA, headers=headers).status_code == 403
        assert client.get("/api/camadas-externas", headers=headers).status_code == 200


def test_escrita_em_camadas_externas_gera_auditoria(client, usuario_coordenador):
    """RF-13: `camadas_externas` recebe escrita pela API, então também precisa de trilha (migração 0002)."""
    headers = cabecalho_auth(usuario_coordenador)
    camada_id = client.post("/api/camadas-externas", json=CAMADA, headers=headers).json()["id"]
    client.patch(f"/api/camadas-externas/{camada_id}", json={"ativa": False}, headers=headers)

    registros = client.get(
        "/api/auditoria", params={"tabela": "camadas_externas", "registro_id": camada_id}, headers=headers
    ).json()
    operacoes = sorted(r["operacao"] for r in registros)
    assert operacoes == ["INSERT", "UPDATE"]
    atualizacao = next(r for r in registros if r["operacao"] == "UPDATE")
    assert atualizacao["dados_antes"]["ativa"] is True
    assert atualizacao["dados_depois"]["ativa"] is False
    assert all(r["usuario_id"] == str(usuario_coordenador.id) for r in registros)

from tests.conftest import cabecalho_auth


def _criar_recurso(client, headers, orgao_id, nome="Viatura de Teste"):
    payload = {
        "tipo": "equipamento",
        "nome": nome,
        "orgao_id": str(orgao_id),
        "especialidade": "transporte",
        "capacidade_valor": 10,
        "capacidade_unidade": "pessoas",
        "localizacao": {"type": "Point", "coordinates": [-40.3128, -20.3155]},
    }
    resposta = client.post("/api/recursos", json=payload, headers=headers)
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def test_cadastro_recurso_aparece_disponivel(client, orgao, usuario_coordenador):
    headers = cabecalho_auth(usuario_coordenador)
    recurso = _criar_recurso(client, headers, orgao.id)
    assert recurso["estado"] == "disponivel"
    assert recurso["localizacao"]["type"] == "Point"


def test_transicao_estado_valida(client, orgao, usuario_coordenador, usuario_operador):
    recurso = _criar_recurso(client, cabecalho_auth(usuario_coordenador), orgao.id)

    resposta = client.patch(
        f"/api/recursos/{recurso['id']}/estado",
        json={"estado": "indisponivel"},
        headers=cabecalho_auth(usuario_operador),
    )
    assert resposta.status_code == 200
    assert resposta.json()["estado"] == "indisponivel"


def test_transicao_estado_invalida_e_rejeitada(client, orgao, usuario_coordenador):
    headers = cabecalho_auth(usuario_coordenador)
    recurso = _criar_recurso(client, headers, orgao.id)

    # disponivel -> empenhado só pode acontecer via /api/empenhos, nunca
    # diretamente pelo PATCH de estado (RF-02: rejeitar transição inválida).
    resposta = client.patch(f"/api/recursos/{recurso['id']}/estado", json={"estado": "empenhado"}, headers=headers)
    assert resposta.status_code == 409
    assert "transição" in resposta.json()["detail"].lower() or "estado" in resposta.json()["detail"].lower()


def test_inativar_recurso_empenhado_e_bloqueado(client, orgao, ocorrencia_aberta, usuario_coordenador, usuario_operador):
    headers_coord = cabecalho_auth(usuario_coordenador)
    recurso = _criar_recurso(client, headers_coord, orgao.id)

    resposta_empenho = client.post(
        "/api/empenhos",
        json={"recurso_id": recurso["id"], "ocorrencia_id": ocorrencia_aberta["id"]},
        headers=cabecalho_auth(usuario_operador),
    )
    assert resposta_empenho.status_code == 201

    resposta = client.delete(f"/api/recursos/{recurso['id']}", headers=headers_coord)
    assert resposta.status_code == 409

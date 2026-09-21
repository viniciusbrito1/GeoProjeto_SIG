from tests.conftest import cabecalho_auth


def test_consulta_pode_listar_recursos(client, usuario_consulta):
    resposta = client.get("/api/recursos", headers=cabecalho_auth(usuario_consulta))
    assert resposta.status_code == 200


def test_consulta_nao_pode_cadastrar_recurso(client, orgao, usuario_consulta):
    payload = {
        "tipo": "equipamento",
        "nome": "Não deveria existir",
        "orgao_id": str(orgao.id),
        "localizacao": {"type": "Point", "coordinates": [-40.3, -20.3]},
    }
    resposta = client.post("/api/recursos", json=payload, headers=cabecalho_auth(usuario_consulta))
    assert resposta.status_code == 403


def test_operador_nao_pode_cadastrar_recurso_mestre(client, orgao, usuario_operador):
    """RF-12: Operador tem escrita restrita — cadastro mestre de recursos é só do Coordenador."""
    payload = {
        "tipo": "equipamento",
        "nome": "Não deveria existir",
        "orgao_id": str(orgao.id),
        "localizacao": {"type": "Point", "coordinates": [-40.3, -20.3]},
    }
    resposta = client.post("/api/recursos", json=payload, headers=cabecalho_auth(usuario_operador))
    assert resposta.status_code == 403


def test_operador_pode_alterar_estado_recurso(client, orgao, usuario_coordenador, usuario_operador):
    payload = {
        "tipo": "equipamento",
        "nome": "Recurso RBAC",
        "orgao_id": str(orgao.id),
        "localizacao": {"type": "Point", "coordinates": [-40.3, -20.3]},
    }
    recurso = client.post("/api/recursos", json=payload, headers=cabecalho_auth(usuario_coordenador)).json()

    resposta = client.patch(
        f"/api/recursos/{recurso['id']}/estado", json={"estado": "indisponivel"}, headers=cabecalho_auth(usuario_operador)
    )
    assert resposta.status_code == 200


def test_consulta_nao_acessa_auditoria(client, usuario_consulta):
    resposta = client.get("/api/auditoria", headers=cabecalho_auth(usuario_consulta))
    assert resposta.status_code == 403


def test_sem_token_e_rejeitado(client):
    resposta = client.get("/api/recursos")
    assert resposta.status_code == 401

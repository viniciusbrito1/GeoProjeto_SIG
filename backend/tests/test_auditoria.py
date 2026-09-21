from tests.conftest import cabecalho_auth


def test_escrita_gera_trilha_de_auditoria(client, orgao, usuario_coordenador):
    headers = cabecalho_auth(usuario_coordenador)
    payload = {
        "tipo": "equipamento",
        "nome": "Recurso Auditado",
        "orgao_id": str(orgao.id),
        "localizacao": {"type": "Point", "coordinates": [-40.3, -20.3]},
    }
    recurso = client.post("/api/recursos", json=payload, headers=headers).json()

    auditoria = client.get("/api/auditoria", params={"tabela": "recursos", "registro_id": recurso["id"]}, headers=headers)
    assert auditoria.status_code == 200
    registros = auditoria.json()
    assert len(registros) == 1
    assert registros[0]["operacao"] == "INSERT"
    assert registros[0]["dados_depois"]["nome"] == "Recurso Auditado"
    assert registros[0]["usuario_id"] == usuario_coordenador.id.__str__()


def test_auditoria_nao_tem_endpoint_de_escrita(client, usuario_coordenador):
    """RF-13: a trilha é só leitura pela aplicação — não existe rota de escrita."""
    headers = cabecalho_auth(usuario_coordenador)
    assert client.post("/api/auditoria", json={}, headers=headers).status_code == 405
    assert client.delete("/api/auditoria", headers=headers).status_code == 405

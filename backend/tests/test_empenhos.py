from tests.conftest import cabecalho_auth


def _criar_recurso(client, headers, orgao_id):
    payload = {
        "tipo": "equipe",
        "nome": "Equipe SAR Teste",
        "orgao_id": str(orgao_id),
        "localizacao": {"type": "Point", "coordinates": [-40.3128, -20.3155]},
    }
    resposta = client.post("/api/recursos", json=payload, headers=headers)
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def test_empenhar_e_liberar_ciclo_completo(client, orgao, ocorrencia_aberta, usuario_coordenador, usuario_operador):
    recurso = _criar_recurso(client, cabecalho_auth(usuario_coordenador), orgao.id)
    headers_op = cabecalho_auth(usuario_operador)

    empenho = client.post(
        "/api/empenhos", json={"recurso_id": recurso["id"], "ocorrencia_id": ocorrencia_aberta["id"]}, headers=headers_op
    )
    assert empenho.status_code == 201
    assert empenho.json()["status"] == "ativo"

    recurso_apos = client.get(f"/api/recursos/{recurso['id']}", headers=headers_op).json()
    assert recurso_apos["estado"] == "empenhado"

    liberacao = client.post(f"/api/empenhos/{empenho.json()['id']}/liberar", headers=headers_op)
    assert liberacao.status_code == 200
    assert liberacao.json()["status"] == "liberado"

    recurso_final = client.get(f"/api/recursos/{recurso['id']}", headers=headers_op).json()
    assert recurso_final["estado"] == "disponivel"


def test_duplo_empenho_e_impossivel(client, orgao, ocorrencia_aberta, usuario_coordenador, usuario_operador):
    """OBJ-3: 'Duplo empenho impossível pelo sistema'."""
    recurso = _criar_recurso(client, cabecalho_auth(usuario_coordenador), orgao.id)
    headers_op = cabecalho_auth(usuario_operador)
    corpo = {"recurso_id": recurso["id"], "ocorrencia_id": ocorrencia_aberta["id"]}

    primeiro = client.post("/api/empenhos", json=corpo, headers=headers_op)
    assert primeiro.status_code == 201

    segundo = client.post("/api/empenhos", json=corpo, headers=headers_op)
    assert segundo.status_code == 409
    assert "empenhad" in segundo.json()["detail"].lower()


def test_duplo_empenho_bloqueado_mesmo_no_banco(db_session, orgao, ocorrencia_aberta, usuario_coordenador, usuario_operador):
    """A regra não pode depender só da camada de serviço: o índice único
    parcial `uq_empenho_ativo_por_recurso` tem que barrar mesmo um INSERT
    feito direto contra o banco, ignorando a API inteira."""
    import uuid

    from sqlalchemy.exc import IntegrityError

    from app.models.empenho import Empenho
    from app.models.enums import TipoRecurso
    from app.models.recurso import Recurso
    from app.services.geo import geojson_para_geometria

    recurso = Recurso(
        id=uuid.uuid4(),
        tipo=TipoRecurso.equipe,
        nome="Recurso Teste Direto",
        orgao_id=orgao.id,
        geom=geojson_para_geometria({"type": "Point", "coordinates": [-40.3, -20.3]}),
    )
    db_session.add(recurso)
    db_session.commit()

    ocorrencia_id = uuid.UUID(ocorrencia_aberta["id"])
    db_session.add(Empenho(recurso_id=recurso.id, ocorrencia_id=ocorrencia_id, autor_empenho_id=usuario_operador.id))
    db_session.commit()

    db_session.add(Empenho(recurso_id=recurso.id, ocorrencia_id=ocorrencia_id, autor_empenho_id=usuario_operador.id))
    try:
        db_session.commit()
        assert False, "esperava IntegrityError do índice único parcial"
    except IntegrityError as exc:
        assert "uq_empenho_ativo_por_recurso" in str(exc.orig)
        db_session.rollback()


def test_nao_pode_empenhar_recurso_indisponivel(client, orgao, ocorrencia_aberta, usuario_coordenador, usuario_operador):
    headers_op = cabecalho_auth(usuario_operador)
    recurso = _criar_recurso(client, cabecalho_auth(usuario_coordenador), orgao.id)

    client.patch(f"/api/recursos/{recurso['id']}/estado", json={"estado": "indisponivel"}, headers=headers_op)

    resposta = client.post(
        "/api/empenhos", json={"recurso_id": recurso["id"], "ocorrencia_id": ocorrencia_aberta["id"]}, headers=headers_op
    )
    assert resposta.status_code == 409

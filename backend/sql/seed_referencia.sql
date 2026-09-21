-- Dados de referência mínimos para o sistema operar (não são dados de teste de
-- carga — para isso ver backend/app/seed/seed_escala.py, que atende RNF-10).
-- Amostra de municípios do Espírito Santo com código IBGE real; para produção,
-- carregue a tabela completa de municípios do IBGE.

INSERT INTO municipios (codigo_ibge, nome, uf) VALUES
    ('3205309', 'Vitória', 'ES'),
    ('3205200', 'Vila Velha', 'ES'),
    ('3201308', 'Cariacica', 'ES'),
    ('3205002', 'Serra', 'ES'),
    ('3201209', 'Cachoeiro de Itapemirim', 'ES'),
    ('3203205', 'Linhares', 'ES'),
    ('3201506', 'Colatina', 'ES'),
    ('3202405', 'Guarapari', 'ES')
ON CONFLICT (codigo_ibge) DO NOTHING;

INSERT INTO orgaos (id, nome, sigla) VALUES
    (gen_random_uuid(), 'Defesa Civil Estadual do Espírito Santo', 'DCE-ES'),
    (gen_random_uuid(), 'Corpo de Bombeiros Militar do Espírito Santo', 'CBMES'),
    (gen_random_uuid(), 'Exército Brasileiro', 'EB'),
    (gen_random_uuid(), 'Polícia Militar do Espírito Santo', 'PMES'),
    (gen_random_uuid(), 'Serviço de Atendimento Móvel de Urgência', 'SAMU')
ON CONFLICT (sigla) DO NOTHING;

-- RF-15: camada WMS externa de exemplo, para o mapa já consumir uma fonte de
-- fora na primeira subida. Hidrografia do IBGE — relevante para chuvas acima da
-- média. Se o provedor estiver fora do ar, o mapa continua funcionando e o
-- painel de camadas mostra "indisponível". Camadas adicionais: menu
-- "Camadas externas" (perfil Coordenador).
INSERT INTO camadas_externas (nome, url_wms, nome_camada, ativa)
SELECT 'Hidrografia (IBGE)', 'https://geoservicos.ibge.gov.br/geoserver/wms', 'CCAR:Hidrografia_2016', TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM camadas_externas
    WHERE url_wms = 'https://geoservicos.ibge.gov.br/geoserver/wms' AND nome_camada = 'CCAR:Hidrografia_2016'
);

# Manual de instalação

Escrito para quem está vendo este projeto pela primeira vez, numa máquina
limpa, sem ajuda da equipe de desenvolvimento (RNF-07: até 60 minutos usando
só esta documentação).

## 1. Pré-requisitos (≈10 min, depende da velocidade de download)

- Docker Engine 24+ e o plugin Docker Compose (`docker compose version` deve
  funcionar). Instaladores oficiais: <https://docs.docker.com/engine/install/>.
- Git, para clonar o repositório (ou o `.zip` baixado pelo botão **Code → Download ZIP** do GitHub).
- `openssl` (já vem instalado por padrão em Linux/macOS; no Windows, use o
  Git Bash que acompanha o Git for Windows).
- Portas 80 e 443 livres na máquina (produção); se algo mais já usa essas
  portas, ajuste o mapeamento `ports:` do serviço `proxy` em
  `docker-compose.yml`.

## 2. Obter o código (≈1 min)

```bash
git clone https://github.com/viniciusbrito1/GeoProjeto_SIG.git
cd GeoProjeto_SIG
```

Repositório: <https://github.com/viniciusbrito1/GeoProjeto_SIG>. Se você baixou o `.zip`, apenas extraia e entre na pasta.

## 3. Configurar segredos (≈5 min)

```bash
cp .env.example .env
```

Abra `.env` num editor de texto e **troque todos os valores** — em
particular `POSTGRES_PASSWORD`, `APP_DB_PASSWORD`, `JWT_SECRET`,
`ADMIN_SENHA` e `GEOSERVER_ADMIN_PASSWORD`. Para gerar valores aleatórios:

```bash
openssl rand -hex 24
```

`ADMIN_EMAIL`/`ADMIN_SENHA` serão o primeiro login do sistema (perfil
Coordenador) — guarde-os.

## 4. Gerar certificado HTTPS (≈1 min)

```bash
bash scripts/gerar_certificado_dev.sh
```

Isso cria um certificado **autoassinado** em `nginx/certs/` — suficiente
para HTTPS funcionar (RNF-06) em homologação/demonstração. O navegador vai
mostrar um aviso de "conexão não segura" porque o certificado não foi
emitido por uma autoridade reconhecida; isso é esperado. Para produção,
substitua `nginx/certs/siscoord.crt` e `siscoord.key` por um certificado
emitido de verdade (Let's Encrypt/certbot, ou o da ICP do seu órgão) e
reinicie o serviço `proxy`.

## 5. Subir o sistema (≈15-30 min na primeira vez — baixa e constrói as imagens)

```bash
docker compose up -d --build
```

Acompanhe a subida (opcional):

```bash
docker compose logs -f
```

A ordem de inicialização é automática: `postgis` fica saudável → `backend`
aplica as migrações, carrega os dados de referência e cria o usuário
Coordenador inicial → `geoserver` sobe → `geoserver-init` publica as camadas
WMS/WFS e termina → `frontend`/`proxy` ficam disponíveis.

## 6. Verificar que subiu (≈2 min)

```bash
docker compose ps
```

Todos os serviços (exceto `geoserver-init`, que termina e fica "Exited (0)"
— isso é esperado) devem aparecer como `running`/`healthy`.

Checagens diretas:

```bash
curl -k https://localhost/api/health
# {"status":"ok","srid":4674}

# console do GeoServer: a porta 8080 só responde na própria máquina do servidor
curl -u admin:<GEOSERVER_ADMIN_PASSWORD> http://localhost:8080/geoserver/rest/about/version.json

# camadas OGC pelo proxy (RF-11): sem credencial → 401; com usuário do sistema → XML de capacidades
curl -k -o /dev/null -w "%{http_code}\n" "https://localhost/geoserver/siscoord/wms?service=WMS&request=GetCapabilities"
curl -k -u "<ADMIN_EMAIL>:<ADMIN_SENHA>" "https://localhost/geoserver/siscoord/wms?service=WMS&version=1.3.0&request=GetCapabilities" | head -5
```

Abra `https://localhost` no navegador e entre com `ADMIN_EMAIL`/`ADMIN_SENHA`
do `.env`.

A documentação interativa da API (Swagger) fica em `https://localhost/api/docs`.
As portas 8000 (API) e 8080 (GeoServer) são publicadas só no loopback do host
(`127.0.0.1`): de outra máquina, use sempre `https://<servidor>/...` (RNF-06).

### Acessar as camadas pelo QGIS (RF-11)

1. *Camada → Adicionar camada → Adicionar camada WMS/WMTS* → **Novo**.
2. URL: `https://<servidor>/geoserver/siscoord/wms` (para WFS: `.../siscoord/wfs`).
3. Em **Autenticação → Básica**, informe e-mail e senha de um usuário ativo do
   SISCOORD-DC (qualquer perfil).
4. Com certificado autoassinado, marque para ignorar erros de SSL nas opções
   de conexão (ou instale um certificado real — passo 4).

### Camada WMS externa (RF-15)

A instalação já cadastra uma camada externa de exemplo — **Hidrografia (IBGE)**
— que aparece no painel do mapa em "Camadas externas". Para cadastrar outras,
entre como Coordenador e use o menu **Camadas externas**. Para demonstrar que o
sistema continua funcionando com o provedor fora do ar, cadastre uma camada com
URL inexistente (ex.: `https://provedor-inexistente.invalid/wms`), ligue-a no
mapa e confira o aviso "(indisponível)"; depois, inative-a na mesma tela.

## 7. (Opcional) Dados de exemplo para teste de escala — RNF-10

```bash
docker compose exec backend python -m app.seed.seed_escala --recursos 600 --ocorrencias 25
```

## 8. Rodar os testes automatizados (≈2 min)

```bash
docker compose exec backend pytest -v
```

## Backup e restauração (RNF-06)

**Backup:**

```bash
bash scripts/backup.sh                    # gera backup_AAAAMMDD_HHMMSS.dump
```

**Restauração** (substitui os dados atuais — cuidado):

```bash
bash scripts/restore.sh backup_20260101_120000.dump
```

**Provar que o backup realmente restaura** (não só "rodou sem erro" — cria
um banco descartável, restaura ali, compara contagem de linhas com o
original, e descarta; nunca toca no banco em uso):

```bash
bash scripts/testar_backup_restore.sh
```

Rode esse último script pelo menos uma vez antes de ir para produção — é
isso que "restauração comprovadamente testada" quer dizer.

## Solução de problemas

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| `docker compose ps` mostra `backend` reiniciando em loop | banco ainda não aceita conexões, ou senha errada no `.env` | `docker compose logs backend`; confira se `APP_DB_PASSWORD` é igual nos dois lugares onde aparece no `.env` |
| Navegador mostra "conexão não seg­ura" | certificado autoassinado (esperado em dev) | ignore em homologação, ou instale um certificado real (passo 4) |
| Mapa não mostra nenhum recurso/ocorrência | banco vazio (normal em instalação nova) | cadastre pelo frontend, ou rode a seed de escala (passo 7) |
| `geoserver-init` com status `Exited (1)` | GeoServer ainda não tinha subido, ou senha do GeoServer errada | `docker compose logs geoserver-init`; depois `docker compose up geoserver-init` para tentar de novo (é idempotente) |
| Camada WMS externa (RF-15) não aparece no mapa | provedor externo fora do ar, ou URL/nome de camada errados no cadastro | o resto do sistema continua funcionando normalmente — entre como Coordenador e confira a URL e o nome da camada no menu "Camadas externas" |
| Camadas "WMS: recursos/ocorrências" do GeoServer não aparecem no mapa | sessão OGC não foi aberta (ex.: login feito antes da atualização) | clique em "Sair" e entre de novo — o login grava o cookie que libera `/geoserver` |
| QGIS recebe `401` ao adicionar a camada WMS/WFS | credencial ausente ou usuário inativo | configure autenticação Básica com e-mail e senha de um usuário **ativo** do sistema |
| `http://<servidor>:8000` ou `:8080` não abre de outra máquina | comportamento esperado: essas portas só escutam no `127.0.0.1` do servidor (RNF-06) | use `https://<servidor>/api/docs` para a API e as URLs `https://<servidor>/geoserver/...` para as camadas |

## Desligar / remover

```bash
docker compose down          # para os containers, mantém os dados (volumes)
docker compose down -v       # para e APAGA os dados — cuidado
```

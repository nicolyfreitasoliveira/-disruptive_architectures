# Pipeline de Dados com IoT e Docker

Projeto acadêmico: CSV real → pandas → SQLAlchemy → PostgreSQL em Docker → views SQL → Streamlit e Plotly. Pré-requisitos: Python 3.11+ (ambiente final testado com Python 3.14), Git e Docker Desktop em execução com Compose v2. Não é necessário instalar PostgreSQL no computador.

## Instalação e execução (PowerShell na raiz)

```powershell
git branch --show-current
# Deve mostrar develop
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
# Edite .env e escolha POSTGRES_PASSWORD; não sobrescreva um .env existente
docker compose up -d --wait
docker compose ps
.\.venv\Scripts\python.exe -m src.pipeline
.\.venv\Scripts\python.exe -m src.verify
.\.venv\Scripts\python.exe -m streamlit run dashboard.py
```

Abra http://localhost:8501. O CSV original `data/IOT-temp.csv` foi fornecido pelo responsável. A fonte é [Temperature Readings: IoT Devices, de Atul Anand Jha](https://www.kaggle.com/datasets/atulanandjha/temperature-readings-iot-devices). A base não é versionada; baixe e extraia o arquivo em `data/` em outro computador. Ajuste `CSV_PATH` no `.env` se mudar o nome. Para reproduzir as versões testadas, instale `requirements-lock.txt`.

## Estrutura

| Arquivo/pasta | Função |
| --- | --- |
| src/config.py | ambiente e conexão sem expor senha |
| src/processing.py | normalização e validação |
| src/pipeline.py | importação em lotes e transação |
| src/database.py | conexão e inicialização |
| src/verify.py | conexão, contagens e views |
| sql/schema.sql | tabelas de leituras e histórico, índices |
| sql/views.sql | agregações SQL |
| dashboard.py | gráficos interativos e exportações CSV |
| docker-compose.yml | PostgreSQL 16, volume e healthcheck |
| tests/ | testes unitários, dashboard e integração opcional |
| docs/ | relatório-base, roteiro e evidências |

## Processamento da base real

| Coluna original | Coluna do banco |
| --- | --- |
| id | source_id (identificador da leitura) |
| room_id/id | device_id (identificador da sala/dispositivo da fonte) |
| noted_date | recorded_at |
| temp | temperature |
| out/in | location |

Datas são interpretadas como dia-mês-ano hora:minuto; horários originais são preservados sem conversão de fuso. A unidade não é presumida no dashboard. Identificadores de salas não comprovam número de sensores físicos. Colunas canônicas e datas ISO sem fuso também são aceitas.

O pipeline rejeita datas, números e identificadores inválidos, sem criar valores nem remover leituras arbitrariamente. O CSV é lido em lotes de `CSV_CHUNK_SIZE`. Uma transação desfaz toda a importação em caso de erro. SHA-256 evita reimportar o mesmo arquivo; arquivos diferentes são importações independentes e podem conter sobreposição. O histórico registra origem, hash, quantidade e horário. Leituras repetidas no arquivo são preservadas.

## Views e dashboard

Auditoria integral CSV × PostgreSQL aprovada: 97.606 registros, 86 datas com leituras dentro de 134 dias corridos. Há uma linha duplicada no original, preservada. Room Admin é o único identificador de sala; não prova um único sensor físico. A unidade não foi confirmada na fonte e não é rotulada como °C. Consulte [auditoria detalhada](docs/auditoria-dados.md). Para repetir: `python -m src.audit_database` com o Python do ambiente virtual.

| View | Agregação | Visualização |
| --- | --- | --- |
| avg_temp_por_dispositivo | AVG e COUNT por device_id | barras de média |
| leituras_por_hora | COUNT pela hora do dia (0–23), em todo o período | linha de contagem |
| temp_max_min_por_dia | MAX e MIN por data | duas linhas de extremos |

O dashboard consulta as três views, mostra quantidades, permite baixar resultados e atualizar dados (cache de 60 segundos). Horas sem leituras não são preenchidas. Banco vazio/indisponível apresenta orientação.

## Testes e consultas

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall -q src dashboard.py tests
.\.venv\Scripts\python.exe -m src.verify
docker compose exec postgres psql -U iot -d iot -c "SELECT COUNT(*) FROM temperature_readings;"
docker compose exec postgres psql -U iot -d iot -c "SELECT * FROM avg_temp_por_dispositivo;"
docker compose exec postgres psql -U iot -d iot -c "SELECT * FROM leituras_por_hora ORDER BY hora;"
docker compose exec postgres psql -U iot -d iot -c "SELECT * FROM temp_max_min_por_dia ORDER BY data LIMIT 5;"
```

Substitua usuário/banco se mudar `.env`. A verificação compara contagens de histórico, leituras e view por hora e exige banco não vazio. Para integração, configure `TEST_DATABASE_URL` com URL SQLAlchemy PostgreSQL de um banco exclusivo de testes e permissão para criar schemas. O teste usa schema isolado e reverte a transação; fixtures não são resultados acadêmicos. Sem essa variável o teste é ignorado. A configuração deve permanecer apenas na sessão local, nunca no código.

Na validação final, **12 testes passaram, sem testes ignorados**, usando um banco de teste temporário separado, removido ao final. `pip check` não encontrou incompatibilidades. A auditoria integral confirmou as 97.606 linhas e todas as linhas das três views. A reexecução do pipeline reconheceu o arquivo já importado, sem duplicação. O dashboard foi testado com o PostgreSQL real e observado no navegador. Veja [resultados finais](docs/validacao.md).

Para encerrar mantendo dados: `docker compose down`. Para erros: `docker compose logs postgres`. Se 5432 estiver ocupada, mude `POSTGRES_PORT`. Alterar senha no `.env` não muda a senha de um volume já inicializado. O banco fica exposto somente em localhost. Credenciais, CSV e ambiente virtual são ignorados no Git.

## Comandos Git

O trabalho permanece em `develop`. A finalização autoriza commit e push exclusivamente para origin/develop; não há merge ou push para main. Os comandos de inspeção e publicação são:

```powershell
git status
git diff
git add .
git commit -m "Implementa pipeline IoT e dashboard"
git push -u origin develop
```

`git init` inicia um novo repositório; aqui já existe um. `git remote add origin URL` configura um remoto se necessário. `git pull --ff-only origin develop` atualiza a branch quando o trabalho estiver salvo. Para autoria local: `git config user.name "Seu Nome"` e `git config user.email "seu@email"`; não é necessário alterar configurações globais.

## Limitações conhecidas

- `temp` não tem unidade confirmada; não se afirma °C ou Fahrenheit.
- `room_id/id` identifica sala; a base não informa identificador individual de sensor físico.
- Média e extremos reúnem ambientes In e Out.
- São 86 datas com leituras em 134 dias corridos; lacunas não foram preenchidas.
- Uma duplicata original foi preservada: 97.606 registros, 97.605 IDs distintos.
- A hora agrega todo o período e não representa frequência regular de aquisição.
- O Docker CLI não estava disponível no terminal da finalização; conexão PostgreSQL 16.15 (Alpine), importação existente, idempotência e views foram verificadas diretamente. A configuração Compose foi revisada, mas os comandos Compose devem ser conferidos no Docker Desktop local.

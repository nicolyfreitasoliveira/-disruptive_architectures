

# Validação final em 07/10/2026

## Resultados executados

| Verificação | Resultado real |
| --- | --- |
| PostgreSQL | Conexão OK; PostgreSQL 16.15 em Linux Alpine |
| Importação existente | Uma importação do CSV original, com 97.606 registros |
| Reexecução do pipeline | Arquivo já importado; mesmo SHA-256; sem duplicação |
| Comparação integral | Todos os campos das 97.606 linhas iguais ao CSV |
| Três views | Todas as linhas iguais às agregações independentes do CSV |
| Dias com leituras | 86 datas em 134 dias corridos inclusivos |
| pytest com banco de teste | 12 testes aprovados em 5,45 segundos; nenhum ignorado |
| pip check | Sem dependências incompatíveis |
| compileall | Fontes compiladas sem erros |
| Dashboard AppTest com PostgreSQL real | Três gráficos e três métricas, sem erros |
| Dashboard no navegador | Três gráficos observados; capturas reais salvas |
| PDF | Gerado, renderizado e inspecionado; três capturas incorporadas |
| Integridade do CSV | SHA-256 inalterado em relação à auditoria anterior |

O teste de integração usa banco temporário separado, criado para esta execução e removido ao final. A transação do teste também reverte seu schema e suas fixtures. Foram verificados inserção, idempotência, valores das três views e rollback após registro inválido. A base acadêmica permaneceu intacta.

O executável Docker não estava disponível no terminal desta etapa. O Compose foi revisado, mas `docker compose config`, `ps` e `up` não foram executados pelo agente. O PostgreSQL em execução respondeu diretamente. Conferir o container e o Compose no Docker Desktop antes da gravação.

O servidor de captura foi iniciado em 127.0.0.1:8502 para não interferir com uma execução existente em 8501. As capturas foram feitas com o recurso de tela cheia do próprio Streamlit. Não houve geração de gráficos substitutos nem alteração de valores.

## Evidências e reprodução

- auditoria-postgresql.json: comparação integral e hash.
- auditoria-csv.json: estatísticas independentes do arquivo.
- auditoria-dados.md: interpretação e limitações.
- screenshots/: resumo e três gráficos reais.
- ../output/pdf/relatorio-academico.pdf: relatório final.

```powershell
.\.venv\Scripts\python.exe -m src.audit_database
.\.venv\Scripts\python.exe -m src.verify
.\.venv\Scripts\python.exe -m src.pipeline
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pip check
```

Sem TEST_DATABASE_URL o teste de integração é ignorado intencionalmente; os outros 11 testes executam. Para reproduzir os 12, configurar a variável somente na sessão local com a URL de um banco exclusivo de teste. Nunca publicar credenciais dessa variável.

## Limitações e pendências humanas

- Unidade de temp não confirmada; sem rótulo Celsius ou conversão.
- Room Admin identifica sala, sem identificação individual de sensor físico.
- Uma duplicata original preservada; 97.605 IDs distintos.
- 48 datas sem leituras; nenhum preenchimento artificial.
- Preencher identificação acadêmica da capa, regenerar PDF e conferir dados pessoais.
- Gravar/publicar vídeo de até quatro minutos e inserir link real da entrega.
- Confirmar acesso público ao repositório e usar o link da branch develop.

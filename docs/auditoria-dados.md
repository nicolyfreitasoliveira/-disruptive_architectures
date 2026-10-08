# Auditoria de fidelidade dos dados — 07/10/2026

Executada contra o CSV original local e o PostgreSQL configurado em .env. Consultas somente leitura; nenhuma linha alterada, descartada ou gerada.

## Origem e comparação integral

Arquivo: data/IOT-temp.csv. SHA-256: `2bf965701db96cd5788403d395a25d2dd7282bea24e317b7f7b157b7a02063d4`.

O histórico contém exatamente uma importação com esse hash e 97.606 leituras. Cada uma das 97.606 linhas foi comparada, na ordem original, pelos campos source_id, device_id, recorded_at, temperature e location. Todos coincidem. O parser de auditoria usa csv.DictReader e datetime.strptime, independentemente da função normalize do pipeline.

As três views foram comparadas integralmente com agregações independentes do CSV. Contagens e extremos coincidem exatamente; médias coincidem com tolerância numérica de 1e-12. O dashboard usa apenas essas consultas PostgreSQL para gráficos e métricas. Os testes com substituição de consultas são restritos a tests/ e não fazem parte da execução da aplicação.

## Identificação correta

A coluna room_id/id contém somente `Room Admin`, sem outros valores. Esse campo identifica a sala, não um sensor físico único. id identifica registros de leitura e não deve virar identificador de dispositivo. out/in contém Out (77.261 linhas) e In (20.345 linhas); são classificações de ambiente, não identificadores físicos individuais.

Foi corrigida a nomenclatura da métrica e do eixo do dashboard e acrescentada uma explicação sob o gráfico exigido de média por dispositivo. A coluna SQL device_id foi mantida para compatibilidade com o enunciado, com semântica esclarecida. Nenhum dispositivo foi inventado.

## Contagens e datas

- CSV e banco: 97.606 linhas.
- Identificadores de leitura distintos: 97.605. Há uma linha integralmente duplicada no CSV, preservada no banco; por isso contagem de registros não equivale a quantidade de IDs únicos.
- Datas distintas com leituras: 86.
- Intervalo: 28/07/2018 07:06 até 08/12/2018 09:30.
- Dias corridos inclusivos no intervalo: 134; 48 datas sem leituras.
- Datas interpretadas como dia-mês-ano, sem conversão de fuso ou preenchimento de lacunas.

## Unidade

O CSV tem a coluna temp, sem metadados de unidade. Não foi possível confirmar Celsius ou Fahrenheit na documentação primária acessível do Kaggle. A descrição de coluna acessível no Kaggle apenas identifica leituras de temperatura. Artigos ou exemplos de terceiros não bastam para atribuir unidade à base original.

Os eixos agora indicam explicitamente unidade não confirmada. Não houve conversão dos valores. Média: 35,05393111079237; mínimo: 21; máximo: 51, todos na escala original.

Fontes consultadas: https://www.kaggle.com/datasets/atulanandjha/temperature-readings-iot-devices e o explorador da mesma fonte no notebook https://www.kaggle.com/koheimuramatsu/iot-temperature-forecasting/data. A página principal não forneceu conteúdo textual ao acesso automatizado; não foi presumida uma unidade.

## Gráficos

1. Barras: média por room_id/id (uma barra), reunindo In e Out; média igual à do CSV.
2. Linha por hora: 24 contagens, agrupadas pela hora do dia em todo o período; soma igual a 97.606.
3. Extremos diários: 86 datas, máximos e mínimos reunindo In e Out, iguais aos do CSV. Marcadores e legenda explicativa distinguem registros de segmentos entre dias ausentes.

Evidência estruturada: docs/auditoria-postgresql.json. Reprodução: `.venv/Scripts/python.exe -m src.audit_database`. Esse comando não altera o banco; grava apenas o resultado da auditoria no repositório.

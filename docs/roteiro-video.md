# Roteiro — 3min50s

| Tempo | Fala e demonstração |
| --- | --- |
| 0:00–0:25 | Identificar integrantes e apresentar objetivo do pipeline IoT. |
| 0:25–0:55 | Mostrar estrutura e fluxo; citar Python, pandas, SQLAlchemy, Docker, PostgreSQL, Streamlit e Plotly. |
| 0:55–1:25 | Mostrar Kaggle e CSV real; explicar mapeamento, validação, transação e hash. Exibir saída real do pipeline. |
| 1:25–1:50 | Mostrar docker compose ps e src.verify com banco e views funcionais. Evitar credenciais na gravação. |
| 1:50–2:20 | Demonstrar barras de média e citar um resultado observado. |
| 2:20–2:50 | Demonstrar leituras por hora e explicar agregação por hora do dia. |
| 2:50–3:20 | Demonstrar extremos diários, amplitude real e limitações dos ambientes. |
| 3:20–3:50 | Mostrar README, concluir com uso prático e link público do código. |

Antes de gravar: executar a base real no banco, verificar dados e preparar conclusões sustentadas. Não usar fixtures como resultados. Publicar no YouTube público/não listado ou rede permitida e conferir acesso ao link sem autenticação. Duração máxima: quatro minutos.

## Falas sugeridas para Nicoly

**0:00–0:25 — mostrar título e resumo do dashboard.**
“Olá, sou Nicoly. Neste trabalho desenvolvi um pipeline para processar leituras históricas de temperatura de IoT. A proposta é transformar um CSV real do Kaggle em dados organizados no PostgreSQL e em três gráficos interativos.”

**0:25–0:55 — mostrar as pastas src, sql e o arquivo Compose.**
“Usei Python e pandas no processamento, SQLAlchemy na conexão com o banco e Docker Compose na configuração do PostgreSQL. O dashboard usa Streamlit e Plotly. O fluxo começa no CSV, passa pela validação e armazenamento, e termina nas consultas das views e nos gráficos.”

**0:55–1:25 — mostrar origem Kaggle e terminal do pipeline.**
“A base contém 97.606 registros. As datas são interpretadas como dia, mês e ano. O pipeline valida os campos, insere em uma transação e usa o hash do arquivo para evitar importar novamente o mesmo conteúdo. Esta mensagem mostra que o arquivo já está importado. A duplicata existente no original foi preservada.”

**1:25–1:50 — mostrar verificação e auditoria.**
“A auditoria comparou todos os registros do PostgreSQL com o CSV e todas as linhas das três views com cálculos independentes. Não houve divergência. Os 12 testes finais passaram, incluindo inserção, reimportação e rollback em um banco de teste separado.”

**1:50–2:20 — mostrar gráfico de barras e apontar Room Admin.**
“Esta barra representa a média, aproximadamente 35,05, na escala original. Room Admin é o identificador de sala disponível, não um identificador individual de sensor. Por isso existe somente uma barra, reunindo os registros internos e externos. A unidade de temperatura não foi confirmada, então não afirmo graus Celsius.”

**2:20–2:50 — mostrar gráfico por hora e pico de 14h.**
“A segunda view conta leituras por hora do dia, somando todo o período. Às 14 horas há o maior volume, 7.248 registros. Isso descreve a distribuição dos registros, sem provar regularidade de aquisição ou a causa dessa diferença.”

**2:50–3:20 — mostrar extremos diários e marcadores.**
“O terceiro gráfico apresenta máximas e mínimas por data. Há 86 datas com leituras em um intervalo de 134 dias corridos. O mínimo global é 21 e o máximo é 51, sem conversão de unidade. A maior amplitude diária foi 28 em 16 de outubro de 2018. Não preenchi datas ausentes.”

**3:20–3:50 — mostrar README, relatório e link develop.**
“O pipeline preserva a base original e disponibiliza consultas e visualizações reproduzíveis. Pode apoiar acompanhamento ambiental e investigação de extremos, mas o uso operacional exige confirmar unidade, fuso e identificação dos sensores. O código, a documentação e o relatório estão no repositório, na branch develop. Obrigada.”

## Preparação da tela

1. Abrir o dashboard em localhost:8501 e deixar os três gráficos carregados.
2. Preparar o terminal com `python -m src.pipeline`, `python -m src.verify` e `python -m src.audit_database`, usando .venv. Não mostrar .env ou credenciais.
3. Deixar README e relatório PDF abertos em abas separadas.
4. Se Docker CLI estiver disponível, mostrar `docker compose ps`; caso contrário, mostrar o container no Docker Desktop. Não declarar uma verificação de Compose que não foi executada.
5. Ensaiar com cronômetro; falar os resultados e demonstrar hover ou zoom em um gráfico. Encerrar antes de quatro minutos.
6. Preencher o link real após a publicação: **[URL do vídeo a inserir pela aluna]**.

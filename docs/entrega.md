# Preparação da entrega pela Nicoly

## Arquivos finais

- Relatório PDF: output/pdf/relatorio-academico.pdf.
- Versão editável: docs/relatorio.md.
- Roteiro com falas e sequência de tela: docs/roteiro-video.md.
- Checklist de requisitos: docs/requisitos.md.
- Instruções de instalação e execução: README.md.
- Validação: docs/validacao.md e docs/auditoria-postgresql.json.
- Capturas reais: docs/screenshots/.

## Abrir e apresentar

1. Abrir o PDF e preencher identificação no Markdown: nome completo, RM, instituição, curso/turma, docente, local/data.
2. Regenerar: instalar requirements-report.txt em .venv e executar `.\.venv\Scripts\python.exe scripts/build_report.py`. Revisar o PDF resultante.
3. Iniciar Docker Desktop e, na raiz, `docker compose up -d --wait`. Conferir `docker compose ps`.
4. Executar `.\.venv\Scripts\python.exe -m src.verify` e `.\.venv\Scripts\python.exe -m src.audit_database`.
5. Abrir `.\.venv\Scripts\python.exe -m streamlit run dashboard.py` e acessar localhost:8501.
6. Gravar conforme o roteiro de 3min50s. Não exibir .env ou senhas. Publicar em modo público ou não listado e conferir o link sem login.
7. Enviar PDF, link do vídeo e link do código em develop. Não precisa fazer merge em main.

Em outro computador, seguir instalação do README e baixar o CSV Kaggle: o arquivo não é enviado ao GitHub. Se o CSV já estiver importado, o pipeline identifica seu hash e não duplica registros.

## Links de entrega

- Código: https://github.com/nicolyfreitasoliveira/-disruptive_architectures/tree/develop
- Dataset: https://www.kaggle.com/datasets/atulanandjha/temperature-readings-iot-devices
- Vídeo: **[preencher URL real após gravação e publicação]**.

Conferir acesso público do código e do vídeo. Não alterar configurações do repositório sem autorização. Credenciais, arquivos temporários e .venv permanecem locais.

# Eleições Brasil 2026 na mídia — exploração visual do GDELT GKG

Projeto de Visualização de Informação (Segundo Caso: exploração de um domínio com
sistema construído a partir de bibliotecas prontas).

## Estrutura

```
projeto/
├── preprocess.py      # parquet bruto do BigQuery -> tabelas limpas em dados/
├── nucleo.py          # carga, filtros e agregações (compartilhado)
├── app.py             # dashboard interativo (Streamlit + Plotly)
├── figuras.py         # figuras estáticas do relatório + estatisticas.json
├── dados/             # gerado por preprocess.py
├── .streamlit/        # tema claro do dashboard
└── relatorio/
    ├── relatorio.tex  # artigo no template IEEE (IEEEtran), em português
    ├── estatisticas.json
    └── figuras/       # PDFs (matplotlib) e capturas do dashboard
```

## Como executar

```bash
pip install -r requirements.txt
python preprocess.py          # ~1 min; lê ../data/raw/gkg_*.parquet
streamlit run app.py          # abre http://localhost:8501
python figuras.py             # regenera as figuras do relatório
```

## Relatório

`relatorio/relatorio.tex` usa a classe `IEEEtran` (template oficial IEEE de
conferência). Para compilar sem instalar LaTeX: crie um projeto no Overleaf,
envie `relatorio.tex` e a pasta `figuras/`, e compile com pdfLaTeX.
Preencha nome, disciplina e instituição no bloco `\author`.

## Decisões importantes de tratamento

* **Páginas automáticas do g1** (`resultado-das-eleicoes-2026…`, `…zona-eleitoral…`):
  13.423 registros excluídos por padrão (há um controle no dashboard para reincluí-los).
* **Menção a atores** = nome em `V2Persons` (com variantes de tradução normalizadas)
  **ou** no slug da URL — o NER do GDELT quase não reconhece "Lula".
* **Mídia nacional** = domínio `.br` ou texto original em português (exceto .pt/.ao/.mz/.cv).
* Datas em **UTC** (como na fonte), para que todos os dias fiquem completos.

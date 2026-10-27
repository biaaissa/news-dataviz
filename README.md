# Enquadramento das enchentes no RS (2024) em fontes nacionais × internacionais

Projeto de visualização de dados com base no [GDELT](https://www.gdeltproject.org/) (Global Knowledge Graph, GKG 2.1).

Esta versão contém apenas a etapa de **extração**. Limpeza, métricas e visualizações serão adicionadas.

## Pergunta

Como grupos distintos de fontes (nacionais × internacionais) enquadram o mesmo evento em **tom, temas, emoções e atores**?

"Enquadramento" é medido por *proxies* do GDELT, não pela análise jornalística de conteúdo. 

## Dimensões e campos usados

| Dimensão | Campo GKG | Observação |
|---|---|---|
| Tom | `V2Tone` | Baseado em dicionário. Interessa a diferença relativa entre grupos. |
| Temas | `V2Themes` | Comparar proporções por grupo, não contagens brutas. |
| Emoções | `GCAM` | Dicionários de emoção; cobertura variável. Indicativo, não verdade. |
| Atores | `V2Persons`, `V2Organizations` | Exigem normalização de nomes. |
| Apoio | `V2Locations`, `TranslationInfo` | Filtro de relevância e marcação de textos traduzidos. |

## Recorte

- **Evento:** enchentes no Rio Grande do Sul, 2024
- **Janela:** 27/04/2024 a 27/05/2024 (fase aguda e de resgate)
- **Decisão de custo:** a janela foi limitada para reduzir o volume lido no BigQuery (~120 GB estimados em dry run). A reconstrução de longo prazo **não** está coberta.
- **Extração propositalmente ampla** (localização OU URL, termos em português e inglês). A relevância é refinada na etapa de limpeza, com funil de contagens.

## Estrutura

```
.
├── README.md
├── requirements.txt
├── .gitignore
├── notebooks/
│   └── 01_extracao.ipynb      # dry run, extração única, checagens iniciais
└── data/
    └── raw/                   # Parquet + JSON de metadados (ver "Dados")
```



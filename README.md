# Enquadramento das eleições no Brasil (2026) em fontes nacionais × internacionais

Projeto de visualização de dados com base no [GDELT](https://www.gdeltproject.org/) (Global Knowledge Graph, GKG 2.1).

A cobertura de eventos extremos pode apresentar variações significativas dependendo da origem do veículo de comunicação. Neste projeto, investigamos como grupos distintos de fontes (nacionais versus internacionais) enquadram as eleições no Brasil de 2026 em relação a **tom, temas, emoções e atores**.

Esta versão contém apenas a etapa de **extração**. Nas etapas subsequentes serão adicionadas a limpeza de dados, o cálculo de métricas e a construção de visualizações comparativas.

## Pergunta

Como grupos distintos de fontes (nacionais × internacionais) enquadram as eleições no Brasil de 2026 em **tom, temas, emoções e atores**?

"Enquadramento" é medido por *proxies* disponibilizadas pelo GDELT (como V2Tone, V2Themes e GCAM), não pela análise jornalística de conteúdo.

## Dimensões e campos usados

| Dimensão | Campo GKG | Observação |
|---|---|---|
| Tom | `V2Tone` | Baseado em dicionário. Interessa a diferença relativa entre grupos. |
| Temas | `V2Themes` | Comparar proporções por grupo, não contagens brutas. |
| Emoções | `GCAM` | Dicionários de emoção; cobertura variável. Indicativo, não verdade. |
| Atores | `V2Persons`, `V2Organizations` | Exigem normalização de nomes. |
| Apoio | `V2Locations`, `TranslationInfo` | Filtro de relevância e marcação de textos traduzidos. |

## Recorte

- **Evento:** eleições no Brasil, 2026
- **Janela:** 01/10/2026 a 30/10/2026
- **Extração propositalmente ampla**: (tema `ELECTION` **E** localização no Brasil) **OU** URL com termos de eleição em português, inglês e espanhol. A relevância é refinada na etapa de limpeza, com funil de contagens.
- **Custo:** a cobrança no BigQuery depende das colunas lidas e dos dias varridos, não do filtro. O notebook faz *dry run* e aplica um teto (`MAX_GB`) antes de executar a query.

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

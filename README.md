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

## Configuração do ambiente

O notebook é o mesmo em Linux, WSL e Windows: a pasta `data/raw` é resolvida a partir da raiz do projeto, independente de onde o Jupyter foi aberto. Só a instalação muda.

> **Antes de extrair de novo:** a extração de 01–30/10/2026 lê cerca de **90 GB** no BigQuery. Se alguém do grupo já tem o `.parquet` + `.json` em `data/raw/`, copie os dois arquivos para a sua `data/raw/`: o notebook detecta o raw e pula a query (não precisa de conta no Google Cloud para a exploração).

### 1. Projeto no Google Cloud

- Contas institucionais (ex.: `@unesp.br`) **não podem criar projetos**; use uma conta pessoal do Gmail.
- Crie um projeto, ative a API do BigQuery e ajuste `PROJECT` na célula de configuração do notebook com o **ID** do projeto (é único globalmente).
- Os primeiros 1 TiB de consulta por mês são gratuitos.

### 2a. Windows (PowerShell ou Anaconda Prompt)

```powershell
# gcloud CLI (ou use o instalador: https://cloud.google.com/sdk/docs/install)
winget install --id Google.CloudSDK -e
# feche e abra o terminal para o comando gcloud ser reconhecido

# Ambiente Python
conda create -n news_dataviz python=3.12 -y
conda activate news_dataviz
pip install -r requirements.txt

# Projeto e credenciais (substitua SEU_PROJECT_ID)
gcloud auth login
gcloud projects create SEU_PROJECT_ID          # pule se já criou pelo console
gcloud config set project SEU_PROJECT_ID
gcloud services enable bigquery.googleapis.com
gcloud auth application-default login
gcloud auth application-default set-quota-project SEU_PROJECT_ID
```

As credenciais usadas pelo Python ficam em `%APPDATA%\gcloud\application_default_credentials.json`.

### 2b. Linux / WSL

```bash
# gcloud CLI sem sudo, instalado na home
curl -sSLO https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz
tar -xzf google-cloud-cli-linux-x86_64.tar.gz -C ~ && rm google-cloud-cli-linux-x86_64.tar.gz
echo 'source ~/google-cloud-sdk/path.bash.inc' >> ~/.bashrc && source ~/.bashrc

conda create -n news_dataviz python=3.12 -y && conda activate news_dataviz
pip install -r requirements.txt

# mesmos comandos gcloud da seção Windows
```

No WSL o navegador não abre sozinho: copie a URL exibida no terminal para o navegador do Windows. As credenciais ficam em `~/.config/gcloud/application_default_credentials.json`.

### 3. Rodar

Abra `notebooks/01_extracao.ipynb` com o kernel `news_dataviz` e execute em ordem. Problemas comuns:

- **`DefaultCredentialsError`**: faltou o `gcloud auth application-default login` (é diferente do `gcloud auth login`). Na tela de consentimento do Google, **marque todas as caixas** de permissão, inclusive a de acesso aos dados do Google Cloud. Depois, **reinicie o kernel**.
- **`Project ... not found or permission denied`**: o `PROJECT` do notebook não existe ou pertence a outra conta. Confira com `gcloud projects list`.

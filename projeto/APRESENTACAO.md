# Eleições Brasil 2026 na mídia — dados, insights e roteiro de apresentação

> Material de apoio para a apresentação de até 30 minutos do projeto de Visualização de Informação.
> Todos os números vêm de `relatorio/estatisticas.json`, gerado por `figuras.py`.

---

## Parte 1 — Os dados analisados

### 1.1 De onde vêm

| Item | Valor |
|---|---|
| **Fonte** | GDELT Global Knowledge Graph 2.0 (GKG), via Google BigQuery (`gdelt-bq.gdeltv2.gkg_partitioned`) |
| **O que é o GDELT** | Projeto que lê continuamente notícias online do mundo todo, em mais de 100 idiomas, e extrai automaticamente temas, pessoas, organizações, locais e tom |
| **Período** | 01/10/2026 a 30/10/2026 (UTC); 1º turno em **04/10** e 2º turno em **25/10** |
| **Critério de seleção** | Notícias com o tema `ELECTION` **e** menção ao Brasil, **ou** com URL contendo termos eleitorais (`eleic`, `segundo-turno`, `brazil…election`, `brasil…elección` etc.) |
| **Registros brutos** | 95.422 (95.403 após remover duplicatas) |
| **Registros analisados** | **81.980**, após excluir 13.423 páginas automáticas |
| **Veículos** | 3.924 |
| **Idiomas de origem** | 60; principais: português 42.685, espanhol 14.651, inglês 11.516, alemão 2.084 |
| **Mídia internacional** | 49,1% dos artigos analisados |

### 1.2 O que cada notícia traz (campos usados)

| Campo GKG | O que contém | Como foi usado |
|---|---|---|
| `DataHora` | Momento da publicação/coleta (a cada 15 min) | Séries temporais diárias e horárias |
| `Veiculo` / `URL` | Domínio e endereço da notícia | Ranking de veículos, separação nacional × internacional, detecção de candidatos no *slug* e tabela com links |
| `V2Tone` | Tom e outras 6 medidas de sentimento | Tom médio por dia, mídia, ator, tema, UF e idioma |
| `V2Themes` | Temas de uma taxonomia com mais de 2.000 códigos (ex.: `CORRUPTION`, `ELECTION_FRAUD`) | Mapa de calor da agenda; 30 temas traduzidos para o português |
| `V2Persons` / `V2Organizations` | Pessoas e organizações citadas | Visibilidade dos candidatos e rede de coocorrência |
| `V2Locations` | Locais citados, com país, código de estado (FIPS) e coordenadas | Mapa por UF e países mencionados |
| `TranslationInfo` | Idioma original (quando foi traduzido) | Idioma de origem e classificação da mídia |
| `GCAM` | Milhares de dimensões emocionais | **Não usado** (proposto como trabalho futuro) |

### 1.3 O que é o "tom"

**tom = % de palavras positivas − % de palavras negativas** do texto, segundo um dicionário de sentimento.
Vai de cerca de −10 a +10; o noticiário costuma ser levemente negativo (mediana ≈ −0,5).
Ele mede o **vocabulário emocional da notícia**, não a opinião do jornalista sobre um candidato, por isso serve
para **comparar** grupos e períodos.

### 1.4 Tratamentos feitos

1. **Exclusão de páginas automáticas:** 13.423 URLs do g1 no formato *"resultado das eleições 2026 em [cidade] – votação para presidente na [escola]"*.
2. **Normalização de nomes:** a tradução automática gera variantes, que foram unificadas ("Luiz Inacio Lula", "Luis Ignacio Lula", "Lewis Lula" → **Lula**; "Andrew Mendonca" → André Mendonça; "Guillaume Boulos" → Guilherme Boulos). Entidades que não são pessoas e créditos de fotógrafos foram removidos.
3. **Detecção de candidatos:** um artigo cita um ator se o nome está em `V2Persons` **ou** na URL.
4. **Nacional × internacional:** domínio `.br` ou texto em português = nacional, exceto Portugal, Angola, Moçambique e Cabo Verde.
5. **Tabelas "longas":** os campos com várias entradas por notícia viraram tabelas artigo–tema, artigo–pessoa, artigo–UF etc. (≈ 3,3 milhões de linhas), o que torna os filtros do dashboard instantâneos.

---

## Parte 2 — Insights

### Insight 1 — A visualização encontrou um erro nos dados
- **O que se viu:** picos enormes em 5–6/10 e 26/10, e o `globo.com` muito afastado dos demais veículos no gráfico de tom (+2,16, quando todos os outros grandes veículos ficam entre −1,1 e +0,1).
- **Causa (descoberta na aba Artigos):** 13.423 páginas geradas por robô com o resultado de cada seção eleitoral. O tom delas é **+3,12** porque são textos curtos com palavras como "escola" e "votação".
- **Por que importa:** sem o filtro, três conclusões sairiam erradas: o volume dos dias de apuração, o tom da mídia nacional e a visibilidade dos candidatos.
- **Mensagem:** a exploração visual também serve para **auditar a qualidade dos dados**.

### Insight 2 — O GDELT "não enxerga" o Lula
- Só **17%** das menções a Lula vêm do campo de pessoas; 89% são recuperadas pela URL. Para Jair Bolsonaro, 99% vêm do campo de pessoas.
- O reconhecedor de nomes falha com nomes de uma palavra só ("Lula"). Usando apenas o campo de pessoas, Lula pareceria **5 vezes menos citado** que Flávio Bolsonaro.
- Pelo mesmo motivo, as menções a "Jair Bolsonaro" na mídia nacional (119) estão subestimadas: a imprensa brasileira costuma escrever só "Bolsonaro".

### Insight 3 — A cobertura tem dois ciclos, e o 2º turno é mais internacional
- O volume atinge o máximo **no dia seguinte** a cada votação (5/10 e 26/10; pico de 10.230 artigos em 26/10) e cai rapidamente.
- Entre os turnos ficam ~1.000–2.000 artigos por dia, com quedas nos fins de semana.
- A mídia internacional representa **42%** da cobertura no 1º turno, **64%** no 2º turno e **71%** no pós-eleição.

### Insight 4 — A imprensa estrangeira é mais negativa
- Tom médio: **nacional −0,45 × internacional −1,58**, e a nacional fica acima **em todos os 30 dias**.
- A diferença é significativa (Mann–Whitney, p < 0,001) e tem efeito moderado (d de Cohen = 0,45).
- Idiomas mais negativos: francês (−2,60), alemão (−2,06) e inglês (−1,94). Menos negativos entre os estrangeiros: russo (−0,67) e espanhol (−1,15).
- As duas mídias chegam perto do neutro **nos dias de votação**, quando a cobertura é procedimental (comparecimento, apuração).

### Insight 5 — Os atores centrais e o tom associado
| Ator | Artigos | Tom (nacional) | Tom (internacional) |
|---|---|---|---|
| Flávio Bolsonaro | 27.325 | −0,67 | −1,55 |
| Lula | 26.631 | −0,40 | −1,25 |
| Jair Bolsonaro | 12.751 | −1,34 | −1,77 |
| Donald Trump | 8.516 | −1,05 | −2,15 |

- Flávio liderou a visibilidade no 1º turno, **Lula dominou o pico do 2º turno** e Flávio volta a liderar no pós-eleição.
- Lula aparece nas notícias de tom menos negativo nas duas mídias; Trump, nas mais negativas da mídia internacional.
- Candidatos derrotados no 1º turno (Caiado, Zema, Renan Santos) ficaram abaixo de 600 artigos cada.

### Insight 6 — A agenda muda a cada fase
| Fase | Temas em destaque |
|---|---|
| Pré-1º turno / 1º turno | Educação, Emprego (temas programáticos e procedimentais) |
| Entre turnos | **Economia (24%)** e **Preços (20%)**; degrau de Corrupção em **19/10** (primeiro debate e troca de desafios sobre quebra de sigilos bancários) |
| 2º turno | **Democracia (32%)**, Extremismo, Liberdades políticas |
| Pós-eleição | **Corrupção (até 46% em 28/10)**, **Fraude eleitoral (2% → 12%)**, Julgamento, Prisão |

- Os temas mais negativos são Fraude eleitoral (−2,84), Crime (−2,53) e Corrupção (−2,47).
- **Atenção:** o tema "Florestas/rios" aparece em 30–45% dos artigos em todas as fases. Provavelmente é um erro do classificador, que confunde "Rio" (de Janeiro, Grande do Sul…) com rio.

### Insight 7 — O pós-eleição virou notícia internacional
- É a fase **mais negativa** (internacional −2,25; nacional −1,27), e 71% dos artigos são estrangeiros.
- As manchetes tratam da reeleição de Lula, da contestação do resultado por Flávio Bolsonaro, da ida dele aos EUA e de declarações de Trump sobre suposta fraude.
- Trump aparece **90% das vezes em mídia estrangeira** e tem seu pico nessa fase (3.342 artigos).
- ⚠️ Esses fatos vêm das manchetes indexadas, não de fonte oficial; confira com o TSE.

### Insight 8 — Rede e geografia
- **Rede** (35 pessoas, ≥ 40 artigos em comum): o núcleo é formado por Jair Bolsonaro, Flávio, Trump e Lula, cercados por Milei, Sheinbaum, Putin e Netanyahu. A eleição foi lida dentro da **geopolítica das Américas**.
- **Michelle Bolsonaro** tem a maior centralidade de intermediação (0,31): ela "liga" o núcleo a atores do Congresso e do Judiciário (Tebet, Alcolumbre, Dallagnol, André Mendonça).
- **Mapa:** SP (16.130), DF (13.737) e RJ (7.799) concentram as menções; o DF aparece por sediar TSE, STF e governo.
- Pernambuco tem o maior saldo de menções favorável a Lula (+0,20); o DF é o único dos dez estados mais citados com saldo favorável a Flávio.
- **Países mais citados junto à eleição:** EUA (25.401), Argentina (12.552) e Reino Unido (5.432).

---

## Parte 3 — Roteiro com as falas (até 30 minutos)

### Como usar este roteiro

- Cada fala tem um **tempo reservado (⏱)** e o intervalo no cronômetro (**início → fim**).
- As falas dos slides ficam entre **100 e 125 palavras por minuto**, um ritmo calmo, com espaço para pausas. Nas demonstrações ao vivo há menos texto (60 a 110 palavras por minuto), para sobrar tempo para os cliques.
- **[AÇÃO]** indica o que fazer na tela *antes ou durante* a fala.
- Trechos entre colchetes, como [seu nome], devem ser preenchidos.
- Não é preciso decorar palavra por palavra: o importante é cumprir os tempos e passar as ideias em negrito.

### Marcos de controle

Confira o cronômetro nestes pontos. Se estiver atrasado(a), use o *Plano de corte* no fim desta parte.

| Cronômetro | Você deve estar começando… |
|---|---|
| 06:00 | Slide 7 (Extração dos dados) |
| 09:00 | Demonstração: tour do sistema |
| 12:00 | Descoberta 5.1 (o erro nos dados) |
| 18:00 | Descoberta 5.4 (nacional × internacional) |
| 24:00 | Slide 11 (Limitações) |
| 27:00 | Slide 14 (Obrigado/perguntas) |

### Visão geral

| Tempo | Bloco | Telas |
|---|---|---|
| 00:00 – 02:00 | 1. Abertura | Slides 1–2 |
| 02:00 – 06:00 | 2. Fundamentação teórica | Slides 3–6 |
| 06:00 – 09:00 | 3. Dados e pré-processamento | Slides 7–9 |
| 09:00 – 12:00 | 4. Sistema e decisões de design | Demonstração + Slide 10 |
| 12:00 – 24:00 | 5. Descobertas | Demonstração ao vivo |
| 24:00 – 27:00 | 6. Limitações, lições e conclusões | Slides 11–13 |
| 27:00 – 30:00 | 7. Encerramento e perguntas | Slide 14 |

> **Antes de começar:** deixe o dashboard aberto (`streamlit run app.py`), com os filtros no padrão e o botão "Excluir páginas automáticas" **ligado**. Clique uma vez em cada aba para que elas já estejam carregadas. Deixe a pasta `relatorio/figuras/` aberta como plano B.

---

### BLOCO 1 — Abertura (00:00 – 02:00)

#### Slide 1 — Título · ⏱ 40 s (00:00 → 00:40)
**Na tela:** título do trabalho, seu nome e uma imagem do dashboard.

> "Boa tarde a todos. Meu nome é [seu nome] e vou apresentar o meu projeto de Visualização de Informação: a exploração visual da cobertura da imprensa sobre as eleições brasileiras de 2026.
> Em outubro, o Brasil escolheu presidente em dois turnos, nos dias 4 e 25. Nesse mês, quase cem mil notícias, escritas em sessenta idiomas, falaram dessa eleição.
> A pergunta central do trabalho é: **o que a visualização interativa consegue revelar sobre como a imprensa, no Brasil e no mundo, cobriu essa disputa?**"

#### Slide 2 — Perguntas de pesquisa · ⏱ 1 min 20 s (00:40 → 02:00)
**Na tela:** as cinco perguntas (Q1 a Q5).

> "Para responder a isso, defini cinco perguntas.
> A primeira: como o **volume e o tom** da cobertura evoluíram ao longo do mês?
> A segunda: a imprensa **internacional** enquadra a eleição de forma diferente da **nacional**?
> A terceira: quais **atores** dominaram a cobertura, e com que tom?
> A quarta: quais **temas** formaram a agenda em cada fase da eleição?
> E a quinta: como esses atores se **relacionam** entre si, e quais **regiões** do país aparecem mais?
> O trabalho se encaixa no segundo caso do enunciado: em vez de implementar uma técnica nova, construí um sistema com bibliotecas prontas e concentrei o esforço na análise dos dados.
> A apresentação segue essa lógica: primeiro um pouco de teoria, depois os dados e o sistema, e a maior parte do tempo nas descobertas, que vou mostrar ao vivo no dashboard."

---

### BLOCO 2 — Fundamentação teórica (02:00 – 06:00)

#### Slide 3 — Visualização exploratória · ⏱ 1 min (02:00 → 03:00)
**Na tela:** definição de visualização de informação e o mantra de Shneiderman.

> "Começando pela fundamentação. Visualização de informação é o uso de representações visuais interativas para **ampliar a cognição**, ou seja, para nos ajudar a perceber padrões que não veríamos numa tabela.
> Na análise exploratória, a gente não parte de hipóteses prontas: as hipóteses **surgem durante a interação** com os dados.
> O princípio que guiou o projeto foi o mantra de Shneiderman: **visão geral primeiro, depois zoom e filtro, e detalhes sob demanda**.
> O dashboard foi organizado exatamente nessa ordem: no topo, indicadores e séries temporais dão a visão geral; os filtros permitem recortar; e uma tabela com os links das notícias originais oferece os detalhes. Vocês vão ver que essa ordem foi decisiva para as descobertas."

#### Slide 4 — Tipos de dado e interação · ⏱ 1 min (03:00 → 04:00)
**Na tela:** os quatro tipos de dado e as quatro interações (filtrar, derivar, navegar, coordenar).

> "Keim propõe classificar as técnicas de visualização em três eixos: o tipo de dado, a técnica visual e a técnica de interação.
> Este trabalho combina **quatro tipos de dado**: temporal, nas séries de volume e tom; multidimensional, nos temas; relacional, na rede de pessoas; e geográfico, no mapa dos estados.
> Do lado da interação, usei as dinâmicas descritas por Heer e Shneiderman. **Filtrar**, com filtros globais. **Derivar**, criando medidas como o tom médio e o saldo de menções entre candidatos. **Navegar**, com zoom e deslocamento nos gráficos. E **coordenar**: todas as visões respondem ao mesmo conjunto de filtros, então um recorte feito no topo vale para o painel inteiro."

#### Slide 5 — Codificação visual · ⏱ 1 min (04:00 → 05:00)
**Na tela:** pequenos exemplos de linha, mapa de calor, escala divergente, círculos proporcionais e grafo.

> "Para escolher os gráficos, segui Munzner: a codificação depende do tipo de atributo.
> **Quantidades** usam posição e comprimento, que são os canais mais precisos; por isso linhas e barras.
> **Intensidade** usa a luminosidade de uma só cor; por isso os mapas de calor vão do azul claro ao escuro.
> O **tom** tem um zero com significado, então usei uma escala divergente: laranja para negativo, azul-petróleo para positivo e cinza no neutro.
> No **mapa**, preferi círculos proporcionais a pintar os estados, porque estados enormes como o Amazonas dominariam visualmente mesmo com poucas menções.
> E a **rede** é desenhada por um algoritmo de forças, com as comunidades detectadas por modularidade."

#### Slide 6 — GDELT e o tom · ⏱ 1 min (05:00 → 06:00)
**Na tela:** logo/descrição do GDELT e a conta do exemplo de tom.

> "A fonte dos dados é o **GDELT**, um projeto que lê continuamente notícias do mundo inteiro, em mais de cem idiomas, e extrai automaticamente temas, pessoas, organizações, locais e o tom de cada texto.
> Como o tom aparece muito nesta apresentação, vale explicar. O GDELT tem dicionários de palavras positivas e negativas. O tom é o **percentual de palavras positivas menos o percentual de negativas**.
> Por exemplo: um texto de quinhentas palavras, com quinze positivas e vinte negativas, tem três por cento menos quatro por cento, ou seja, **tom menos um**.
> Importante: o tom mede o **vocabulário** da notícia, não a opinião do jornalista. Por isso ele serve para **comparar** grupos e períodos."

---

### BLOCO 3 — Dados e pré-processamento (06:00 – 09:00)

#### Slide 7 — Extração dos dados · ⏱ 1 min (06:00 → 07:00)
**Na tela:** resumo da consulta SQL, o número de registros e um exemplo de registro bruto do campo de locais:
`4#Sao Paulo, Sao Paulo, Brazil#BR#BR27#...#-23.53#-46.61#...`

> "Agora os dados. Fiz uma consulta SQL no **BigQuery**, onde o GDELT fica hospedado. Selecionei as notícias de 1º a 30 de outubro que tinham o tema eleição e mencionavam o Brasil, ou que tinham termos eleitorais no endereço, em português, inglês ou espanhol.
> O resultado foram **95 mil registros**.
> Neste slide há um exemplo de como os dados chegam: cada notícia traz campos empacotados. Este aqui é um local: o tipo, o nome, o país, o código do estado, que é BR27 para São Paulo, e as coordenadas.
> Uma notícia pode ter dezenas de locais, pessoas e temas nesse formato, então o primeiro trabalho foi desempacotar tudo."

#### Slide 8 — Fluxo do sistema · ⏱ 1 min (07:00 → 08:00)
**Na tela:** diagrama BigQuery → Parquet → pré-processamento → módulo de agregação → dashboard e relatório.

> "Este é o fluxo do sistema. Os dados saem do BigQuery em formato Parquet.
> O script de pré-processamento separa os campos e gera **tabelas longas**, em que cada linha liga uma notícia a um tema, a uma pessoa ou a um estado. São cerca de **três milhões e trezentas mil linhas**, e é essa estrutura que deixa os filtros instantâneos.
> Depois, um módulo central faz todas as agregações. Esse mesmo módulo alimenta o **dashboard**, feito em Streamlit e Plotly, e as **figuras do relatório**, feitas em Matplotlib.
> Isso garante que os números que vocês veem no painel são exatamente os mesmos do artigo."

#### Slide 9 — Tratamentos · ⏱ 1 min (08:00 → 09:00)
**Na tela:** os quatro tratamentos, com os exemplos de nomes distorcidos.

> "No pré-processamento, tomei quatro decisões.
> Primeiro, classifiquei cada notícia como **nacional**, se o domínio termina em ponto br ou o texto original é em português, ou como **internacional**.
> Segundo, **normalizei os nomes**. Como quase tudo passa por tradução automática, os nomes chegam distorcidos: Lula vira 'Lewis Lula', André Mendonça vira 'Andrew Mendonca', e Guilherme Boulos vira 'Guillaume Boulos'.
> Terceiro, removi entidades que não são pessoas e créditos de fotógrafos.
> Quarto, mantive as datas em UTC, para que todos os dias fiquem completos.
> Mas houve **mais dois tratamentos importantes, que eu só descobri explorando os dados visualmente**. Esses eu vou mostrar ao vivo."

---

### BLOCO 4 — Sistema e decisões de design (09:00 – 12:00)

#### Demonstração — Tour do sistema · ⏱ 2 min (09:00 → 11:00)

**1.** **[AÇÃO]** Troque para o dashboard e mostre a linha de filtros no topo. · ⏱ 30 s (09:00 → 09:30)
> "Este é o dashboard. Aqui no topo fica uma **única linha de filtros**: período, tipo de mídia, idioma de origem, veículo e um botão para excluir páginas automáticas, que eu explico daqui a pouco. Esses filtros valem para **todas** as abas."

**2.** **[AÇÃO]** No filtro *Mídia*, deixe só "Internacional"; mostre os indicadores mudando; depois volte às duas. · ⏱ 30 s (09:30 → 10:00)
> "Logo abaixo ficam os indicadores. Se eu selecionar só a mídia internacional, vejam que tudo se atualiza: o número de artigos, de veículos, o tom médio. Volto para as duas."

**3.** **[AÇÃO]** Clique rapidamente em cada uma das sete abas. · ⏱ 40 s (10:00 → 10:40)
> "O conteúdo está em sete abas: linha do tempo; candidatos; temas; geografia; rede de atores; veículos e idiomas; e, por último, a tabela de artigos, que leva até a notícia original. É o nível de **detalhes sob demanda**."

**4.** **[AÇÃO]** Volte para *Linha do tempo*; passe o mouse sobre uma barra e dê zoom em um trecho. · ⏱ 20 s (10:40 → 11:00)
> "Todos os gráficos têm tooltip com o valor exato e zoom. E as linhas verticais marcam o primeiro e o segundo turno em todas as visões temporais."

#### Slide 10 — Decisões de design · ⏱ 1 min (11:00 → 12:00)
**Na tela:** Lula = vermelho, Flávio = azul; paleta testada para daltonismo; rótulos diretos; sem dois eixos.

> "Antes das descobertas, três decisões de design.
> A primeira: **a cor segue a entidade, não a posição no ranking**. O Lula é sempre vermelho e o Flávio Bolsonaro sempre azul, em qualquer gráfico e com qualquer filtro; quem aprendeu a cor não é enganado depois.
> A segunda: a paleta foi **validada com um script que simula os três tipos de daltonismo** e mede o contraste com o fundo. Como um dos pares de cores ficou no limite, acrescentei **rótulos diretos** no fim de cada linha, para que a identificação não dependa só da cor.
> A terceira: nenhum gráfico tem dois eixos verticais, porque isso cria correlações que não existem."

---

### BLOCO 5 — Descobertas, ao vivo (12:00 – 24:00)

#### 5.1 — O erro nos dados ⭐ · ⏱ 2 min 30 s (12:00 → 14:30)

**1.** **[AÇÃO]** Aba *Linha do tempo* → **desligue** "Excluir páginas automáticas". · ⏱ 35 s (12:00 → 12:35)
> "Esta é a primeira descoberta, e a mais importante. Quando olhei o volume pela primeira vez, sem nenhum tratamento, apareceram estes picos: **mais de onze mil notícias no dia 5 e catorze mil no dia 26**. Picos são esperados depois da votação, mas esses pareciam grandes demais."

**2.** **[AÇÃO]** Aba *Veículos e idiomas* → aponte o `globo.com` isolado à direita. · ⏱ 35 s (12:35 → 13:10)
> "Ao mesmo tempo, no gráfico de tom por veículo, o globo ponto com aparecia **completamente isolado**, com tom médio de mais dois. Todos os outros grandes veículos ficavam entre menos um e zero. Um único veículo, muito positivo e com volume enorme: isso pedia investigação."

**3.** **[AÇÃO]** Aba *Artigos* → digite `zona-eleitoral` → abra uma das URLs. · ⏱ 40 s (13:10 → 13:50)
> "Então fui para os detalhes. Buscando os endereços, encontrei isto: **milhares de páginas geradas por robô**, uma para cada seção eleitoral, com o título 'resultado das eleições em tal cidade, votação para presidente na escola tal'. São **13.423 páginas**. O tom delas é mais três, porque são textos curtinhos cheios de palavras como 'escola' e 'votação'."

**4.** **[AÇÃO]** **Religue** o botão e volte para *Linha do tempo*. · ⏱ 40 s (13:50 → 14:30)
> "Religando o filtro, os picos voltam ao tamanho real. Sem essa descoberta, eu teria concluído que a mídia nacional foi positiva, que os dias de apuração tiveram muito mais cobertura do que tiveram e que alguns candidatos eram mais citados.
> E reparem que foi exatamente o mantra: **a visão geral mostrou a anomalia, o filtro isolou o veículo e os detalhes mostraram a causa**. A visualização serviu para **auditar os dados**."

#### 5.2 — O GDELT não enxerga o Lula · ⏱ 1 min 30 s (14:30 → 16:00)

**1.** **[AÇÃO]** Aba *Candidatos* → role até o gráfico *Fonte da detecção*. · ⏱ 45 s (14:30 → 15:15)
> "A segunda descoberta também é sobre os dados. Este gráfico mostra de onde vem cada menção: do campo de pessoas do GDELT, em azul, ou do endereço da notícia, em laranja.
> Para Jair Bolsonaro, **noventa e nove por cento** vêm do campo de pessoas. Para o Lula, só **dezessete por cento**. O reconhecedor de nomes do GDELT falha com nomes de uma palavra só, como 'Lula'."

**2.** **[AÇÃO]** Continue no mesmo gráfico. · ⏱ 45 s (15:15 → 16:00)
> "Se eu tivesse usado só o campo de pessoas, que é o mais comum, o Lula pareceria **cinco vezes menos citado** que o Flávio Bolsonaro, o que seria um erro grosseiro. Por isso, considerei que uma notícia cita um candidato se o nome aparece no campo de pessoas **ou** no endereço.
> O mesmo problema afeta 'Bolsonaro' escrito sozinho: na imprensa brasileira, só 119 menções foram atribuídas ao Jair, um número claramente subestimado."

#### 5.3 — Ritmo da cobertura e dos candidatos · ⏱ 2 min (16:00 → 18:00)

**1.** **[AÇÃO]** Aba *Linha do tempo* → gráfico de volume diário. · ⏱ 35 s (16:00 → 16:35)
> "Agora o ritmo da cobertura. Sem as páginas automáticas, ficam **dois ciclos** bem claros. O pico não é no dia da votação, mas **no dia seguinte**: 5 e 26 de outubro, com 10.230 notícias neste último. Entre os turnos, o volume fica entre mil e dois mil por dia, com quedas nos fins de semana."

**2.** **[AÇÃO]** Troque para *Horária* e dê zoom nos dias 25 e 26/10. · ⏱ 25 s (16:35 → 17:00)
> "Na visão por hora, dá para acompanhar a noite de apuração do segundo turno e ver em que momento a cobertura acelera. É o tipo de detalhe que a visão diária esconde."

**3.** **[AÇÃO]** Volte para *Diária*; aba *Candidatos* → gráfico de visibilidade diária. · ⏱ 40 s (17:00 → 17:40)
> "Nos candidatos: o Flávio Bolsonaro, em azul, liderou a visibilidade no **primeiro turno**. No **segundo turno**, o Lula, em vermelho, dominou o pico. E nos dias seguintes o Flávio volta a liderar, por um motivo que eu mostro daqui a pouco.
> Os candidatos derrotados no primeiro turno, como Caiado, Zema e Renan Santos, ficaram abaixo de seiscentas notícias cada."

**4.** **[AÇÃO]** Troque a métrica para *Participação (% dos artigos do dia)*. · ⏱ 20 s (17:40 → 18:00)
> "Se eu trocar para o percentual das notícias de cada dia, o padrão se mantém. Ou seja, não é só efeito do volume total."

#### 5.4 — Nacional × internacional · ⏱ 2 min (18:00 → 20:00)

**1.** **[AÇÃO]** Aba *Linha do tempo* → gráfico de tom diário. · ⏱ 40 s (18:00 → 18:40)
> "Agora a segunda pergunta: nacional contra internacional. A linha azul é a mídia nacional e a laranja, a internacional. A azul fica acima **em todos os trinta dias**. A média nacional é **menos zero vírgula quarenta e cinco**, e a internacional, **menos um vírgula cinquenta e oito**. A diferença é estatisticamente significativa, com efeito moderado.
> As duas se aproximam do neutro nos dias de votação, quando a cobertura fala de comparecimento e apuração."

**2.** **[AÇÃO]** Aba *Veículos e idiomas* → gráfico de idiomas. · ⏱ 30 s (18:40 → 19:10)
> "Por idioma, as coberturas em **francês, alemão e inglês** são as mais negativas. Entre os estrangeiros, **russo e espanhol** são os menos negativos. Isso sugere que não é só efeito da tradução, porque idiomas traduzidos também diferem muito entre si."

**3.** **[AÇÃO]** Role até o histograma de tom. · ⏱ 20 s (19:10 → 19:30)
> "No histograma, dá para ver que não são só alguns casos extremos: a distribuição internacional **inteira** está deslocada para o lado negativo."

**4.** **[AÇÃO]** Aba *Candidatos* → gráfico *Tom por ator e tipo de mídia*. · ⏱ 30 s (19:30 → 20:00)
> "E por candidato: o Lula aparece nas notícias de tom **menos negativo** nas duas mídias. O Trump aparece nas **mais negativas** da imprensa internacional. Lembrando: isso é o clima das notícias em que cada um aparece, não um julgamento sobre a pessoa."

#### 5.5 — A agenda muda a cada fase · ⏱ 2 min (20:00 → 22:00)

**1.** **[AÇÃO]** Aba *Temas* → mapa de calor *Temas por fase*. · ⏱ 40 s (20:00 → 20:40)
> "A quarta pergunta é sobre a agenda. Este mapa de calor mostra o percentual de notícias de cada fase em cada tema.
> Antes e durante o primeiro turno, aparecem temas como **educação e emprego**. Entre os turnos, sobem **economia**, com vinte e quatro por cento, e **preços**, com vinte. No segundo turno, **democracia** chega ao máximo, trinta e dois por cento. E no pós-eleição explodem **corrupção e fraude eleitoral**."

**2.** **[AÇÃO]** Suba até o mapa de calor diário e aponte a linha *Corrupção* no dia 19/10. · ⏱ 30 s (20:40 → 21:10)
> "No mapa diário, vejam este degrau de corrupção no **dia 19**. Indo aos detalhes, ele coincide com o primeiro debate do segundo turno e com uma troca de desafios entre os candidatos sobre **quebra de sigilos bancários**."

**3.** **[AÇÃO]** Mostre o gráfico *Tom associado a cada tema*. · ⏱ 25 s (21:10 → 21:35)
> "O tom por tema é coerente: **fraude eleitoral, crime e corrupção** são os mais negativos, enquanto educação e emprego ficam perto de menos um."

**4.** **[AÇÃO]** Aponte a linha *Florestas/Amazônia* no mapa de calor. · ⏱ 25 s (21:35 → 22:00)
> "Um alerta de interpretação: o tema 'florestas e rios' aparece em trinta a quarenta e cinco por cento das notícias, o tempo todo. Muito provavelmente o classificador confunde '**Rio**', de Rio de Janeiro e Rio Grande do Sul, com rio. É um bom exemplo de por que dados automáticos exigem cuidado."

#### 5.6 — O pós-eleição · ⏱ 1 min (22:00 → 23:00)

**1.** **[AÇÃO]** No filtro *Período*, selecione 27/10 a 30/10. · ⏱ 30 s (22:00 → 22:30)
> "Agora o pós-eleição. Selecionando de 27 a 30 de outubro, vejam os indicadores: **setenta e um por cento** das notícias são estrangeiras, e é a fase **mais negativa** do mês. Corrupção chega a **quarenta e seis por cento** das notícias no dia 28, e fraude eleitoral sobe de dois para doze por cento."

**2.** **[AÇÃO]** Volte o período para o mês inteiro. · ⏱ 30 s (22:30 → 23:00)
> "Pelas manchetes, essas notícias tratam da reação ao resultado: a contestação pelo Flávio Bolsonaro, a ida dele aos Estados Unidos e declarações do Trump sobre suposta fraude. Por isso o Trump tem seu pico nesta fase, quase sempre em mídia estrangeira.
> Ressalto que isso é **o que as manchetes dizem**; o resultado oficial é do TSE."

#### 5.7 — Rede e mapa · ⏱ 1 min (23:00 → 24:00)

**1.** **[AÇÃO]** Aba *Rede de atores* → mexa no controle *Coocorrência mínima* e abra *Comunidades detectadas*. · ⏱ 35 s (23:00 → 23:35)
> "Na rede de pessoas, o tamanho é o número de notícias e as linhas ligam quem aparece junto. No centro estão os Bolsonaro, o Lula e o Trump, cercados por **Milei, Sheinbaum, Putin e Netanyahu**: a eleição foi lida dentro da **geopolítica das Américas**. A Michelle Bolsonaro tem a maior intermediação: ela é a ponte para atores do Congresso e do Judiciário."

**2.** **[AÇÃO]** Aba *Geografia* → selecione *Saldo de menções Lula × Flávio*. · ⏱ 25 s (23:35 → 24:00)
> "No mapa, **São Paulo, Distrito Federal e Rio** concentram as menções; o DF aparece por sediar TSE, STF e governo. Pelo saldo de menções, **Pernambuco** é o estado mais favorável ao Lula, e o DF é o único dos dez mais citados com saldo favorável ao Flávio."

---

### BLOCO 6 — Limitações, lições e conclusões (24:00 – 27:00)

#### Slide 11 — Limitações · ⏱ 1 min (24:00 → 25:00)
**Na tela:** as quatro limitações.

> "Voltando aos slides, as limitações.
> A principal é sobre o **tom**: ele é calculado contando palavras, quase sempre sobre uma tradução automática, e **não sabe a quem o sentimento se dirige**. Uma frase como 'Lula venceu e Flávio sofreu dura derrota' mistura positivo e negativo para pessoas diferentes.
> Segundo, há **erros de tradução e de classificação**, como os nomes distorcidos e o tema das florestas.
> Terceiro, o GDELT **não é uma amostra representativa** de toda a imprensa: ele cobre o que consegue indexar online.
> E, por fim, a divisão entre nacional e internacional por domínio e idioma é uma **aproximação**."

#### Slide 12 — Lições sobre visualização · ⏱ 1 min (25:00 → 26:00)
**Na tela:** as quatro lições.

> "O que eu tiro de lição sobre visualização?
> Primeiro, a **visão geral** foi o que revelou as anomalias: os picos e aquele ponto isolado do globo.
> Segundo, os **detalhes sob demanda** foram essenciais: sem a tabela com os links, eu teria visto o problema, mas não a causa.
> Terceiro, vale **visualizar a qualidade dos próprios dados**: o gráfico de fonte da detecção evitou uma conclusão errada sobre os candidatos.
> E quarto, os **filtros coordenados** permitiram comparar fases e mídias sem refazer nenhum gráfico.
> Em resumo, a visualização não serviu só para mostrar resultados, mas para **chegar neles de forma correta**."

#### Slide 13 — Conclusões · ⏱ 1 min (26:00 → 27:00)
**Na tela:** as três mensagens e os trabalhos futuros.

> "Para concluir, três mensagens.
> Primeira: a exploração visual **encontrou e corrigiu dois problemas sérios** nos dados, as páginas automáticas e o viés contra o nome do Lula.
> Segunda: a **imprensa internacional foi consistentemente mais negativa** que a nacional, e ganhou peso a cada fase da eleição.
> Terceira: a agenda migrou de **propostas para economia, depois para democracia, e terminou em corrupção e fraude**, num pós-eleição tratado como notícia internacional.
> Como trabalhos futuros, quero usar as dimensões emocionais do GDELT, detectar mudanças de padrão automaticamente, analisar o tom frase a frase e comparar com as eleições de 2018 e 2022."

---

### BLOCO 7 — Encerramento (27:00 – 30:00)

#### Slide 14 — Obrigado(a) e perguntas · ⏱ 20 s de fala + até 2 min 40 s de perguntas (27:00 → 30:00)
**Na tela:** "Obrigado(a)!", seu contato e o link ou caminho do código.

> "Muito obrigado(a) pela atenção. O código, o dashboard e o relatório estão disponíveis. Fico à disposição para perguntas."

Use as respostas da seção *Perguntas prováveis*, logo abaixo. Se ninguém perguntar, ofereça à turma uma busca ao vivo na aba **Artigos** (ex.: `debate`, `urna`, `pesquisa`).

---

### Plano de corte (se o tempo encurtar)

| Tempo disponível | O que cortar (e quanto você ganha) |
|---|---|
| **~25 min** | Junte os slides 3 e 4 em um só (−1 min). Em 5.3, pule a fala 2, da visão horária (−25 s). Em 5.4, pule a fala 3, do histograma (−20 s). Em 5.5, pule a fala 4, das florestas (−25 s). Encurte as perguntas para 2 min (−40 s). Total: cerca de 3 min a menos. Ajuste os demais tempos proporcionalmente. |
| **~20 min** | Além do anterior: corte o slide 12, de lições (−1 min). Corte o slide 8, do fluxo (−1 min). Em 5.4, pule a fala 2, dos idiomas (−30 s). Junte 5.6 e 5.7 usando só as falas 5.6-1 e 5.7-1 (−55 s). Encurte o tour do sistema para as falas 1 e 3 (−50 s). |
| **Qualquer duração** | **Nunca corte o 5.1** (erro nos dados) nem o **5.2** (viés do Lula): são as descobertas mais originais do trabalho. |

---

## Perguntas prováveis e respostas curtas

| Pergunta | Resposta |
|---|---|
| *"O tom negativo significa que a imprensa foi contra o candidato?"* | Não. O tom mede o vocabulário do texto inteiro e não identifica o alvo. Ele indica o clima das notícias em que o ator aparece, e serve para comparar. |
| *"Por que não usou um mapa coroplético?"* | Estados grandes como AM e PA dominariam visualmente mesmo com poucas menções. Símbolos proporcionais codificam o volume pela área do círculo, independente do tamanho do estado. |
| *"Como garantiu que as páginas removidas eram mesmo automáticas?"* | Pelo padrão fixo de URL e pela inspeção manual de amostras na aba Artigos; 99,7% delas são do g1. O botão permite comparar com e sem elas. |
| *"A diferença nacional × internacional não é efeito da tradução?"* | Pode haver parte disso; é uma limitação declarada. Mas o padrão aparece também entre idiomas estrangeiros (russo −0,67 contra francês −2,60), o que indica diferença de enquadramento, e não só de tradução. |
| *"Por que Flávio tem mais menções que Lula?"* | Os totais são próximos (27,3 mil × 26,6 mil). O Flávio é muito citado no pós-eleição pela contestação do resultado, e o Lula ainda pode estar subestimado pelo viés de detecção. |
| *"Os resultados da eleição vêm de onde?"* | Das manchetes indexadas pelo GDELT. O trabalho analisa a **cobertura**, não o resultado oficial, que deve ser consultado no TSE. |

## Checklist do dia

- [ ] `streamlit run app.py` testado no computador da apresentação
- [ ] Filtros no padrão e botão de páginas automáticas **ligado** antes de começar
- [ ] Abas que serão usadas já carregadas uma vez (o primeiro carregamento demora alguns segundos)
- [ ] Pasta `relatorio/figuras/` aberta como plano B
- [ ] Ensaiar o bloco 5.1 (é o que mais impressiona e o que tem mais cliques)
- [ ] Cronômetro visível

# Projeto Final de AVD

Projeto final da disciplina de Análise e Visualização de Dados (AVD) 2026.2. A Parte Comum usa o dataset Obesity e a Parte Específica usa o dataset Adult, ambos do UCI Machine Learning Repository.

## Dataset da Parte Comum

Estimation of Obesity Levels Based On Eating Habits and Physical Condition (Obesity), com 2.111 instâncias, 17 atributos e a variável alvo NObeyesdad com 7 classes de nível de obesidade. O arquivo já está no repositório em data/parte_comum/, então não é preciso baixar nada.

Fonte: [UCI Machine Learning Repository: Obesity](https://archive.ics.uci.edu/dataset/544)

## Dataset da Parte Específica

A página oficial do UCI informa 48.842 instâncias, 14 atributos, variáveis categóricas e inteiras, tarefa de classificação e presença de valores ausentes. O alvo é a faixa de renda anual acima ou abaixo de US$ 50 mil. O dataset foi aprovado pela professora.

Fonte: [UCI Machine Learning Repository: Adult](https://archive.ics.uci.edu/dataset/2/adult)  
Referência: Becker, B. & Kohavi, R. (1996). Adult. UCI Machine Learning Repository. DOI: 10.24432/C5XW20.  
Licença informada pelo UCI: CC BY 4.0.

O arquivo CSV é obtido pelo script de download; os arquivos de dados gerados ficam fora do Git.

## Requisitos

- Python 3.11 ou superior.
- Bibliotecas listadas em requirements.txt.

### Instalação

Crie um ambiente virtual e instale as dependências:

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt

## Parte Comum

Os notebooks ficam em notebooks/parte_comum/ e podem ser executados de forma independente:

    jupyter notebook notebooks/parte_comum/eda.ipynb
    jupyter notebook notebooks/parte_comum/kmeans_metricas.ipynb

O eda.ipynb faz a análise exploratória (estrutura, distribuições, relações e outliers). O kmeans_metricas.ipynb faz a padronização, as duas passadas do K-Means (k livre pelo Método do Cotovelo e k fixo igual ao número de classes), as matrizes de confusão e as métricas. Os resultados do K-Means são gravados em out/parte_comum/kmeans/.

## Parte Específica

### Baixar o dataset e gerar tabelas iniciais da EDA

    python src/parte_especifica/download_data.py
    python src/parte_especifica/eda_inicial.py

As tabelas são gravadas em out/parte_especifica/eda/. O script gera apenas tabelas; as interpretações estão em docs/relatorio_template.md.

### Executar a EDA do Adult (notebook)

    jupyter notebook src/parte_especifica/eda.ipynb

As figuras do notebook são gravadas em out/parte_especifica/figuras/. O notebook localiza a raiz do projeto sozinho, então pode ser aberto de qualquer pasta.

### Gerar as seis visualizações

Com o dataset já baixado, execute:

    python src/parte_especifica/visualizacoes.py

Os gráficos (quatro exploratórios e dois explanatórios) são gravados em out/parte_especifica/visualizacoes/.

### Executar o dashboard

Com o dataset local disponivel, execute:

    streamlit run src/parte_especifica/dashboard.py

O aplicativo possui filtros de perfil, indicadores, visualizacoes exploratorias, uma aba dedicada a pergunta de pesquisa e exportacao do recorte filtrado.

## Estrutura

- data/parte_comum/: dataset comum da turma (Obesity, do UCI Machine Learning Repository).
- data/parte_especifica/: dados do Adult obtidos pelo script.
- docs/relatorio_template.md: roteiro para o relatório.
- docs/DECLARACAO_IA.md: rascunho da declaração de uso de IA (exportar assinada como docs/DECLARACAO_IA.pdf para entrega).
- notebooks/parte_comum/: notebooks da Parte Comum (eda.ipynb e kmeans_metricas.ipynb).
- out/: tabelas e figuras geradas pelos notebooks e scripts (versionadas, pois o relatório faz referência a elas). Em out/parte_comum/kmeans/ ficam os resultados do K-Means; em out/parte_especifica/ ficam eda/ (tabelas), figuras/ (EDA) e visualizacoes/ (as seis visualizações).
- src/parte_comum/: pasta alternativa para scripts da Parte Comum (o grupo optou por notebooks).
- src/parte_especifica/: download dos dados, EDA (eda.ipynb e eda_inicial.py), visualizações (visualizacoes.py) e dashboard (dashboard.py).

## Uso de IA

A Inteligência Artificial foi utilizada exclusivamente como apoio técnico ao desenvolvimento do projeto, incluindo organização da estrutura de arquivos, implementação de scripts, preparação dos dados, geração de visualizações e desenvolvimento do dashboard. Os trechos de código produzidos com esse apoio estão identificados nos respectivos arquivos. Todas as decisões analíticas, interpretações dos resultados, escolhas metodológicas, justificativas e conclusões foram revisadas e validadas pelo grupo, que se responsabiliza integralmente pelo conteúdo apresentado e deve ser capaz de explicar cada etapa do projeto.

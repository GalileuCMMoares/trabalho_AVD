# Projeto de AVD — Adult

Estrutura inicial do projeto de Análise e Visualização de Dados. A Parte Específica está preparada para trabalhar com o dataset Adult, do UCI Machine Learning Repository.

## Dataset da Parte Específica

A página oficial do UCI informa 48.842 instâncias, 14 atributos, variáveis categóricas e inteiras, tarefa de classificação e presença de valores ausentes. O alvo é a faixa de renda anual acima ou abaixo de US$ 50 mil. A aprovação do dataset pela professora precisa ser confirmada pelo grupo.

Fonte: [UCI Machine Learning Repository — Adult](https://archive.ics.uci.edu/dataset/2/adult)  
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

### Baixar o dataset e gerar tabelas iniciais da EDA

    python src/parte_especifica/download_data.py
    python src/parte_especifica/eda_inicial.py

As tabelas são gravadas em out/parte_especifica/eda/. O script não cria gráficos nem conclusões: cabe ao grupo interpretar os resultados, definir as visualizações e escrever as notas analíticas.

## Estrutura

- data/parte_comum/: dataset comum da turma (Obesity ou Wine Quality; escolha pendente).
- data/parte_especifica/: dados do Adult obtidos pelo script.
- docs/relatorio_template.md: roteiro vazio para o relatório.
- notebooks/parte_comum/: reservado à implementação da Parte Comum.
- out/: tabelas e resultados gerados.
- src/parte_comum/: reservado aos scripts da Parte Comum.
- src/parte_especifica/: download e tabelas de apoio à EDA.

## Uso de IA

A IA foi usada como apoio técnico para estruturar o projeto e preparar o código de download e de tabelas descritivas. Os trechos correspondentes estão marcados nos arquivos Python. O grupo deve revisar e saber explicar o código, registrar o uso na declaração exigida e produzir por conta própria as interpretações, escolhas de gráficos e conclusões.

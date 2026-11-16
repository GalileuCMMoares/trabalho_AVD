# Relatório — Projeto Final de AVD

## Integrantes e matriz de contribuição

Preencher com os nomes e as contribuições reais.

## Parte Comum

### Dataset e preparação

Registrar a fonte, as decisões de limpeza e a padronização.

### EDA

Preencher a análise estrutural, distribucional, relacional e de outliers. Incluir as visualizações e interpretações escritas pelo grupo.

### K-Means e métricas

Descrever as duas passadas, o mapeamento dos clusters, as matrizes de confusão e as métricas.

### Discussão crítica

Comparar os resultados e discutir a granularidade das classes.

## Parte Específica — Adult

### Pergunta de pesquisa e público-alvo

Preencher pelo grupo.

### Dataset e preparação

**Aprovação e fonte.** Dataset validado pela professora. Fonte: UCI Machine Learning Repository, *Adult* (Becker & Kohavi, 1996; DOI 10.24432/C5XW20; CC BY 4.0). Unimos `adult.data` e `adult.test`, totalizando 48.842 instâncias e 14 atributos mais a classe `income` (`<=50K` ou `>50K`), com variáveis inteiras e categóricas. Removemos espaços extras, o ponto final das classes em `adult.test` e marcamos `?` como ausente (`download_data.py`).

**Valores ausentes.** Três colunas têm ausências: `workclass` (2.799; 5,73%), `occupation` (2.809; 5,75%) e `native-country` (857; 1,75%). No total, 3.620 linhas (7,41%) têm ao menos um ausente. Em `workclass` e `occupation` os ausentes ocorrem quase sempre juntos e não são aleatórios: nessas linhas só 9,5% têm renda `>50K`, contra 24,8% nas demais. Em `native-country` a taxa é parecida (25,7% contra 23,9%).

*Tratamento adotado:* não removemos linhas. Recodificamos os ausentes de `workclass`, `occupation` e `native-country` como a categoria "Desconhecido". Isso preserva 7,4% da base e mantém visível um grupo com perfil próprio de renda; excluir essas linhas enviesaria a análise para empregos formais.

**Duplicatas.** Há 52 linhas totalmente idênticas. Como a base é amostral e não tem identificador, elas podem ser pessoas distintas com o mesmo perfil, e o impacto é desprezível (0,1%); mantivemos.

### EDA

As tabelas de apoio estão em `out/parte_especifica/eda/` (geradas por `src/parte_especifica/eda_inicial.py`).

**1. Estrutura.** 48.842 linhas e 15 colunas: 6 numéricas inteiras (`age`, `fnlwgt`, `education-num`, `capital-gain`, `capital-loss`, `hours-per-week`) e 9 categóricas (incluindo `income`). `education` e `education-num` descrevem a mesma informação (16 níveis); usaremos apenas uma delas por análise. `fnlwgt` é um peso amostral do censo, não uma característica da pessoa, e não será usado como variável explicativa. A classe é desbalanceada: 37.155 (76,1%) `<=50K` e 11.687 (23,9%) `>50K`.

**2. Distribuições.**
- `age`: média 38,6, mediana 37, intervalo 17–90, ligeiramente assimétrica à direita. O valor 90 é um teto da base (186 pessoas com 80 anos ou mais).
- `hours-per-week`: mediana 40 e 46,7% das pessoas trabalham exatamente 40 horas; há caudas em ambos os lados (1.125 com 10 horas ou menos; 528 com 80 ou mais).
- `capital-gain` e `capital-loss`: dominadas por zeros. Só 8,3% têm ganho de capital e 4,7% têm perda; o máximo de ganho (99.999) é um valor de teto e aparece 244 vezes.
- `education-num`: mediana 10 (ensino médio completo e alguma faculdade concentram a maior parte).
- Categóricas: 69,4% trabalham no setor privado, 91,3% nasceram nos EUA, 85,5% são brancos e 66,8% são homens. A amostra é pouco diversa em país de origem e raça, então comparações envolvendo grupos pequenos (por exemplo `Other`, com 406 pessoas) devem ser lidas com cautela.

**3. Relações com a classe.**
- *Idade e horas:* quem ganha `>50K` é mais velho (média 44,3 contra 36,9) e trabalha mais (45,5 contra 38,8 horas por semana), mas as medianas de horas são iguais (40), então a diferença vem da cauda de longas jornadas.
- *Escolaridade:* é o preditor mais forte entre os nominais. A proporção de `>50K` vai de 1% a 16% até o ensino médio, sobe para 41% em bacharelado, 55% em mestrado e passa de 72% em doutorado e escola profissional.
- *Estado civil e parentesco:* casados no civil têm 44,6% de `>50K`; solteiros que nunca casaram, 4,5%. Efeito parcialmente confundido com idade.
- *Ocupação:* varia de 1,2% (serviço doméstico) e 4,1% (outros serviços) a 45,1% (profissionais especializados) e 47,8% (gerência).
- *Sexo e raça:* 30,4% dos homens contra 10,9% das mulheres têm `>50K`. Por raça, asiático-pacífico (26,9%) e branca (25,4%) ficam acima de negra (12,1%) e indígena (11,7%). São associações descritivas na amostra, que não isolam causas (a distribuição por ocupação, idade e horas também difere entre grupos).
- *Capital:* 61,7% de quem tem ganho de capital e 50,1% de quem tem perda estão em `>50K`, contra 20,5% e 22,6% dos demais. Todos os 244 casos com ganho 99.999 são `>50K`.

**4. Outliers.** O critério do IQR (1,5×) sinalizou: `age` 216 (0,44%), `fnlwgt` 1.453 (2,97%), `education-num` 1.794 (3,67%), `capital-gain` 4.035 (8,26%), `capital-loss` 2.282 (4,67%) e `hours-per-week` 13.496 (27,63%).

*Decisão:* mantivemos todos os registros, pelos motivos a seguir.
- Em `capital-gain` e `capital-loss`, Q1 e Q3 são 0, então o IQR é zero e qualquer valor positivo vira "outlier". São casos reais e muito informativos sobre a renda, não erros.
- Em `hours-per-week`, a concentração em 40 horas estreita a faixa (32,5–52,5) e infla a contagem: jornadas de 35 a 60 horas são plausíveis.
- Em `education-num`, os sinalizados são níveis baixos de escolaridade, válidos.
- `age` (até 90) é plausível; o 90 é um teto de codificação.
- `fnlwgt` é peso amostral e não entra na análise.
- O valor 99.999 em `capital-gain` é um código de teto, não um valor exato; será mencionado nas notas dos gráficos.

Para visualização, `capital-gain` e `capital-loss` serão tratados em escala logarítmica ou como indicador (tem/não tem), e a idade e as horas poderão ser agrupadas em faixas. Os testes e modelos, se usados, consideram o desbalanceamento da classe (76/24).

### Storytelling e visualizações

Para cada visualização, registrar o que mostra, o insight extraído e por que foi escolhida. Responder à pergunta de pesquisa.

### Dashboard

Descrever como executar e quais recursos foram implementados.

## Uso de IA

Registrar os usos permitidos, identificar os trechos de código apoiados por IA e anexar a declaração assinada.

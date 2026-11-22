# Relatório — Projeto Final de AVD

## Integrantes e matriz de contribuição

| Integrante | Contribuições no projeto |
|---|---|
| João Pedro Aguiar Morais | Parte Comum: EDA, padronização dos dados, agrupamento com K-Means e análise de métricas. |
| Galileu Calaça Menezes de Moraes | *Descrever as contribuições realizadas no projeto.* |
| Caio Guimarães Rocha | Parte Específica: implementação das visualizações, organização das notas analíticas e desenvolvimento do dashboard interativo em Streamlit. |
| Mateus de Almeida Ribeiro | Parte Específica e organização do projeto: revisão da Parte Específica, organização da estrutura do repositório e conferência de que todas as entregas atendem aos requisitos do projeto. |

## Parte Comum

### Dataset e preparação

Registrar a fonte, as decisões de limpeza e a padronização.

### EDA

Preencher a análise estrutural, distribucional, relacional e de outliers. Incluir as visualizações e interpretações escritas pelo grupo.

### K-Means e métricas

Rodamos o K-Means (`random_state=42`, `n_init=10`) sobre as 8 variáveis numéricas padronizadas, em duas passadas: k = 4, escolhido pelo Método do Cotovelo, e k = 7, o número real de classes. Para avaliar, cada cluster foi mapeado para a classe real majoritária dentro dele; a matriz de confusão compara esse rótulo mapeado com a classe real. Na Passada 1 a matriz é 7×4 (só 4 rótulos possíveis) e na Passada 2 é 7×7. Acurácia, precisão e recall por classe foram calculados a partir da matriz (notebook `kmeans_metricas.ipynb`, figuras em `out/parte_comum/kmeans/`).

| Passada | k | Acurácia | Precisão macro | Recall macro | Classes representadas |
|---|---|---|---|---|---|
| 1 — k livre | 4 | 0,310 | 0,174 | 0,310 | 4/7 |
| 2 — k fixo | 7 | 0,382 | 0,265 | 0,370 | 5/7 |

Baseline (prever sempre a classe mais frequente): acurácia 0,168.

| Classe | Recall P1 | Recall P2 | Precisão P1 | Precisão P2 |
|---|---|---|---|---|
| Insufficient_Weight | 0,764 | 0,461 | 0,292 | 0,346 |
| Normal_Weight | 0,000 | 0,348 | 0,000 | 0,275 |
| Overweight_Level_I | 0,000 | 0,000 | 0,000 | 0,000 |
| Overweight_Level_II | 0,000 | 0,000 | 0,000 | 0,000 |
| Obesity_Type_I | 0,208 | 0,382 | 0,225 | 0,260 |
| Obesity_Type_II | 0,633 | 0,401 | 0,326 | 0,352 |
| Obesity_Type_III | 0,565 | 1,000 | 0,377 | 0,622 |

Na Passada 1, cada cluster recebeu um rótulo diferente (`Insufficient_Weight`, `Obesity_Type_I`, `Obesity_Type_II` e `Obesity_Type_III`), mas a classe majoritária ocupa só 22,5% a 37,7% de cada cluster. Na Passada 2, dois clusters foram mapeados para `Obesity_Type_III` e dois para `Obesity_Type_I`, de modo que `Overweight_Level_I` e `Overweight_Level_II` não são previstas.

### Discussão crítica

#### Qual passada gerou grupos mais coerentes?

Pelas métricas, a Passada 2 (k = 7) foi melhor. A acurácia subiu de 0,310 para 0,382, a precisão média de 0,174 para 0,265 e o recall médio de 0,310 para 0,370. Ela também representa 5 das 7 classes, contra 4 na Passada 1. As duas passadas superam o baseline de 0,168 (prever sempre a classe mais frequente), então os clusters carregam alguma informação sobre o nível de obesidade, mas pouca: na melhor das passadas, quase 2 em cada 3 pessoas caem num cluster cuja classe majoritária não é a sua.

A Passada 1 só não fica tão atrás porque, com menos clusters, cada um "cobre" mais classes vizinhas. A pureza dos clusters mostra isso: na Passada 1 a classe majoritária ocupa entre 22,5% e 37,7% de cada cluster, ou seja, nenhum grupo é dominado por uma classe. Na Passada 2 aparecem grupos mais puros, com destaque para o cluster 3 (71,9% `Obesity_Type_III`) e o cluster 1 (52,5% `Obesity_Type_III`). Por isso consideramos a Passada 2 a mais coerente em relação às classes reais, ainda que coerente aqui signifique "menos misturada", não "bem separada".

O ganho da Passada 2, porém, não é uniforme. `Obesity_Type_III` passa a ter recall 1,0, mas `Insufficient_Weight` cai de 0,764 para 0,461 e `Obesity_Type_II` de 0,633 para 0,401, porque essas classes foram divididas entre mais clusters.

#### Por que algumas classes nunca são previstas?

Na Passada 2, dois pares de clusters receberam o mesmo rótulo (dois viraram `Obesity_Type_III` e dois `Obesity_Type_I`). Sobram só 5 rótulos distintos, e `Overweight_Level_I` e `Overweight_Level_II` nunca são previstas (recall 0 nas duas passadas). Essas pessoas estão espalhadas: `Overweight_Level_II` aparece com 55, 66 e 63 registros nos clusters 0, 2 e 6, e em nenhum deles é maioria. Isso faz sentido porque as faixas de sobrepeso ficam no meio da escala de IMC (cerca de 23 a 30) e se sobrepõem às classes vizinhas em todas as variáveis.

#### O que o K-Means realmente agrupou

Olhando os centroides, os clusters seguem eixos que não são o nível de obesidade:

- *Sexo/altura:* na Passada 2, os clusters 2 e 3 têm peso médio parecido (102 kg e 99 kg), mas o cluster 2 tem altura média de 1,79 m e 3% de mulheres, e o cluster 3 tem 1,65 m e 90% de mulheres. Como o mesmo peso numa pessoa mais baixa gera IMC maior, o cluster masculino fica com maioria `Obesity_Type_II` e o feminino com `Obesity_Type_III`. A separação veio da altura, não do grau de obesidade.
- *Hábitos:* o cluster 4 se diferencia por ter em média 1,2 refeições principais por dia (`NCP`), o cluster 5 pela atividade física alta (`FAF` = 2,1) e o cluster 6 pela idade (37 anos contra cerca de 21–25 nos demais). Nenhum desses eixos coincide com uma faixa de IMC, e por isso esses clusters misturam várias classes.

Ou seja, o K-Means encontrou perfis de estilo de vida e de corpo, que é o que as 8 variáveis descrevem com peso igual, enquanto as classes reais dependem apenas de duas delas (peso e altura, via IMC).

#### Granularidade das classes

As 7 classes são cortes de uma única variável contínua (IMC). As faixas vizinhas são estreitas e sem fronteira natural nos dados: sobrepeso I vai de 22,8 a 28,8 e sobrepeso II de 25,7 a 30,4, por exemplo. Um método não supervisionado não tem como saber onde ficam esses cortes, e as outras 6 variáveis, padronizadas com o mesmo peso, diluem a informação de peso e altura. Os dados parecem sustentar uma divisão mais grosseira (abaixo do peso/normal, sobrepeso, obesidade, obesidade severa) do que as 7 classes, o que também está de acordo com o cotovelo sem dobra nítida.

#### Limitações

- Usamos só as variáveis numéricas; as categóricas (histórico familiar, `FAVC`, transporte, sexo) ficaram de fora e podem ter informação útil.
- Cerca de 77% do dataset foi gerado sinteticamente (SMOTE) pelos autores. Isso explica valores fracionários em variáveis que deveriam ser discretas (`FCVC`, `NCP`, `FAF`, `TUE`, `CH2O`) e pode criar padrões artificiais.
- A escolha de k = 4 foi feita pelo cotovelo, que não tem um ponto de inflexão claro.
- O mapeamento pela classe majoritária permite que vários clusters recebam o mesmo rótulo e deixa classes sem representação, o que penaliza as métricas por classe.
- O K-Means assume grupos esféricos e de tamanho parecido, o que não precisa valer para estes dados.

## Parte Específica — Adult

### Pergunta de pesquisa e público-alvo

**Pergunta de pesquisa.** Como a escolaridade se associa à proporção de pessoas com renda anual acima de US$ 50 mil na base Adult, e como as horas trabalhadas ajudam a contextualizar essa associação?

**Público-alvo.** Equipe de planejamento educacional e empregabilidade que precisa de uma visão inicial dos perfis presentes na amostra. O objetivo é identificar padrões descritivos que merecem investigação adicional; os resultados não demonstram causalidade nem devem embasar decisões individuais.

### Dataset e preparação

**Aprovação e fonte.** Dataset validado pela professora. Fonte: UCI Machine Learning Repository, *Adult* (Becker & Kohavi, 1996; DOI 10.24432/C5XW20; CC BY 4.0). Unimos `adult.data` e `adult.test`, totalizando 48.842 instâncias e 14 atributos mais a classe `income` (`<=50K` ou `>50K`), com variáveis inteiras e categóricas. Removemos espaços extras, o ponto final das classes em `adult.test` e marcamos `?` como ausente (`download_data.py`).

**Valores ausentes.** Três colunas têm ausências: `workclass` (2.799; 5,73%), `occupation` (2.809; 5,75%) e `native-country` (857; 1,75%). No total, 3.620 linhas (7,41%) têm ao menos um ausente. Em `workclass` e `occupation` os ausentes ocorrem quase sempre juntos e não são aleatórios: nessas linhas só 9,5% têm renda `>50K`, contra 24,8% nas demais. Em `native-country` a taxa é parecida (25,7% contra 23,9%).

*Tratamento adotado:* não removemos linhas. Recodificamos os ausentes de `workclass`, `occupation` e `native-country` como a categoria "Desconhecido". Isso preserva 7,4% da base e mantém visível um grupo com perfil próprio de renda; excluir essas linhas enviesaria a análise para empregos formais.

**Duplicatas.** Há 52 linhas totalmente idênticas. Como a base é amostral e não tem identificador, elas podem ser pessoas distintas com o mesmo perfil, e o impacto é desprezível (0,1%); mantivemos.

### EDA

A EDA está em `src/parte_especifica/eda.ipynb`, e as figuras geradas por ele estão em `out/parte_especifica/figuras/`. As tabelas de apoio estão em `out/parte_especifica/eda/` (geradas por `src/parte_especifica/eda_inicial.py`).

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

As seis visualizações estão em `out/parte_especifica/visualizacoes/`. Foram organizadas em quatro peças exploratórias, para entender a base, e duas peças explanatórias, para comunicar a resposta à pergunta de pesquisa.

#### Notas analíticas das visualizações

**1. Distribuição da faixa de renda — exploratória**  

- **O que mostra:** quantidade e percentual das duas classes de renda da base.
- **Insight:** a base é desbalanceada: aproximadamente 76% dos registros estão em `<=50K` e 24% em `>50K`. Por isso, as comparações posteriores usam taxas, e não somente contagens absolutas.
- **Motivo da escolha:** barras comparam duas categorias com clareza e sem distorção visual.

**2. Distribuição de idade por faixa de renda — exploratória**  

- **O que mostra:** distribuição percentual da idade dentro de cada faixa de renda.
- **Insight:** a distribuição de `>50K` tende a se concentrar em idades maiores que a de `<=50K`, mas existe sobreposição entre os grupos. Assim, idade isolada não separa completamente as faixas de renda.
- **Motivo da escolha:** histogramas mostram forma, dispersão e sobreposição de uma variável numérica entre grupos.

**3. Escolaridade por faixa de renda — exploratória**  

- **O que mostra:** mediana, dispersão e extremos de `education-num` em cada classe de renda.
- **Insight:** a distribuição de escolaridade de `>50K` fica deslocada para níveis maiores, embora existam registros dos dois grupos em vários níveis educacionais.
- **Motivo da escolha:** boxplots comparam mediana, quartis e extremos de forma compacta.

**4. Renda acima de US$ 50 mil por ocupação — exploratória**  

- **O que mostra:** proporção de pessoas com renda `>50K` por ocupação, excluindo grupos com poucas observações.
- **Insight:** as taxas variam entre ocupações, apontando ocupação como variável relevante para aprofundamento.
- **Motivo da escolha:** barras horizontais acomodam nomes longos e facilitam ordenar muitas categorias.

**5. Taxa de renda acima de US$ 50 mil por escolaridade — explanatória**  

- **O que mostra:** taxa de `>50K` em cada categoria de escolaridade.
- **Insight:** os níveis mais altos de escolaridade apresentam taxas maiores de renda acima de US$ 50 mil na amostra. Esta é a visualização que responde diretamente à pergunta de pesquisa.
- **Motivo da escolha:** barras ordenadas tornam a comparação entre categorias direta; a cor evidencia o patamar de 40% sem ocultar as demais categorias.

**6. Escolaridade, jornada semanal e renda — explanatória**  

- **O que mostra:** taxa de `>50K` para combinações de escolaridade numérica e faixas de horas trabalhadas por semana.
- **Insight:** a associação com renda alta é mais visível em combinações de maior escolaridade e jornadas mais longas. O tamanho amostral de cada célula deve ser considerado na leitura.
- **Motivo da escolha:** o mapa de calor sintetiza duas dimensões categorizadas e uma medida percentual usando a cor como atributo pré-atentivo.

#### Resposta à pergunta de pesquisa

Na amostra Adult, níveis mais altos de escolaridade estão associados a proporções maiores de pessoas com renda anual acima de US$ 50 mil. Ao combinar escolaridade e jornada semanal, a taxa de renda alta também tende a ser maior nas faixas de jornada mais longas. Esses resultados descrevem associações presentes na base: não demonstram que escolaridade ou horas trabalhadas, isoladamente, causam maior renda, pois idade, ocupação, estado civil e outras características podem estar relacionadas simultaneamente a essas variáveis.

### Dashboard

O dashboard é executado com:

    streamlit run src/parte_especifica/dashboard.py

Ele reúne os indicadores da amostra filtrada, a exploração por ocupação, estado civil, escolaridade e jornada semanal, além de uma aba dedicada à pergunta de pesquisa. Os filtros de sexo, tipo de trabalho, idade e horas por semana atualizam todos os gráficos e indicadores. A aplicação também permite exportar o recorte filtrado em CSV.

## Uso de IA

Registrar os usos permitidos, identificar os trechos de código apoiados por IA e anexar a declaração assinada. Declaração: [Clique aqui](docs\DECLARACAO_IA.md)

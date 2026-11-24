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

**Fonte.** UCI Machine Learning Repository, *Estimation of Obesity Levels Based On Eating Habits and Physical Condition* (ID 544), arquivo `ObesityDataSet_raw_and_data_sinthetic.csv`. São 2.111 instâncias e 17 atributos: 8 numéricos, 8 categóricos e a variável alvo `NObeyesdad`, com 7 classes de nível de obesidade. Não há valores ausentes.

**Limpeza.** Havia 24 linhas duplicadas, que foram removidas, restando 2.087 linhas. Decidimos remover as duplicatas devido a baixa probabilidade de duas pessoas diferentes responderem exatamente igual a 17 perguntas, o que pode configurar envios duplicados de formulario. Além disso, como o número de linhas duplicadas e pequeno, n perdemos volume relevante.

**Padronização.** Como o K-Means nao pode ter acesso aos rotulos reais durante o agrupamento, a coluna `NObeyesdad` foi guardada separada (usada apenas na avaliacao e nas métricas) e aplicamos o `StandardScaler` do `scikit-learn` nas 8 variaveis numéricas.

Essa etapa e necessaria porque o K-Means forma os grupos calculando a distancia euclidiana entre os registros e os centroides. No dataset *Obesity*, as variáveis numericas estao em escalas muito diferentes, por exemplo, `Weight` varia muito mais numericamente (de 39 a 173) do que `NCP`, que varia de 1 a 4. Sem padronizar os dados, as variaveis com escalas numericas diferentes teriam pesos diferentes. As de maior escala dominariam o calculo do K-Means, enquanto as de menor escala teriam peso irrelevante.

Ao aplicar a padronizacao com o `StandardScaler`, todas as variáveis numericas passam a ter media igual a 0 e desvio padrao igual a 1, garantindo que todas tenham o mesmo peso e evitando que o agrupamento seja influenciado desproporcionalmente.

### EDA

As figuras e tabelas desta secao estao no notebook `notebooks/parte_comum/eda.ipynb`.

**1. Estrutura.** O dataset tem 2.111 linhas e 17 colunas, sendo 8 numericas (`Age`, `Height`, `Weight`, `FCVC`, `NCP`, `CH2O`, `FAF`, `TUE`) e 9 categoricas, incluindo a classe `NObeyesdad`. Nao ha valores ausentes, e as 24 linhas duplicadas foram removidas (ver Dataset e preparacao). Na qualidade dos dados, `FCVC`, `NCP`, `CH2O`, `FAF` e `TUE` vem de perguntas com respostas inteiras, mas entre 30,7% e 61,8% dos valores sao fracionarios. Isso e consistente com a informacao do UCI de que cerca de 77% dos registros foram gerados sinteticamente (SMOTE), por interpolacao. Mantivemos essas escalas como numericas, lembrando que os valores intermediarios nao sao respostas reais.

**2. Distribuicoes.**
- `Age` e concentrada em jovens (metade entre 19,9 e 26 anos, mediana 22,85) e tem cauda longa a direita ate 61 anos.
- `Height` e aproximadamente simetrica em torno de 1,70 m, e `Weight` vai de 39 a 173 kg sem um unico pico, o que combina com classes que vao de abaixo do peso ate obesidade tipo III.
- `FCVC`, `CH2O`, `FAF` e `TUE` tem picos nos valores inteiros e valores espalhados entre eles. `NCP` e muito concentrada em 3 refeicoes (cerca de 70% dos registros).
- Varias categoricas sao muito desbalanceadas (`SMOKE` 97,9% nao, `SCC` 95,4% nao, `FAVC` 88,4% sim, historico familiar 82,5% sim, `CAEC` 84,4% Sometimes), e algumas categorias quase nao tem casos (`CALC` Always com 1 registro, `MTRANS` Bike com 7 e Motorbike com 11).
- `Gender` (50,4% homens) e as 7 classes (entre 12,8% e 16,8% cada) sao equilibrados, o que e pouco comum em dados reais e e mais um sinal do balanceamento sintetico.

**3. Relacoes.**
- As correlacoes entre as numericas sao fracas. A maior e entre `Height` e `Weight` (0,46), seguida de `Age` e `TUE` (-0,30) e `Height` e `FAF` (0,29). Nenhum par passa de 0,5, entao nao ha redundancia forte entre as variaveis.
- Com a classe, `Weight` cresce de forma ordenada (media de 50,0 kg em Insufficient_Weight ate 120,9 kg em Obesity_Type_III), como esperado para classes criadas a partir do IMC. `Height` so se destaca em Obesity_Type_II (media de 1,77 m), `Age` e maior em Overweight_Level_II e Obesity_Type_II, e `FAF` cai de forma geral das classes mais leves para as mais pesadas.
- Em Obesity_Type_III, `FCVC` e `NCP` valem 3 para todos os registros, o que nao e esperado em dados reais e provavelmente vem da geracao sintetica.
- Nas categoricas, `Gender` tem a relacao mais forte. Obesity_Type_II e quase so de homens (28% dos homens contra 0,2% das mulheres) e Obesity_Type_III quase so de mulheres (31,2% das mulheres contra 0,1% dos homens), entao nessas classes sexo e grau de obesidade ficam misturados.
- Quem nao tem historico familiar de sobrepeso esta concentrado em Insufficient_Weight (38,9%) e Normal_Weight (35,6%) e nao aparece em Obesity_Type_III. Quem come entre refeicoes com frequencia esta mais em Insufficient_Weight (49,6%), e quem anda a pe esta mais em Normal_Weight (56,4%), mas esta ultima categoria tem poucos registros.

**4. Outliers.** Pelo IQR (1,5 vez), `NCP` teve 577 registros sinalizados (27,65%), `Age` 167 (8,00%) e `Height` e `Weight` 1 cada. Mantivemos todos os registros.
- Em `NCP`, cerca de 70% responderam 3 refeicoes, entao os quartis ficam muito proximos (2,70 e 3,00), o IQR e de 0,30 e os limites ficam entre 2,24 e 3,45. Quem respondeu 1, 2 ou 4 refeicoes vira outlier mesmo sendo uma resposta valida (a pergunta vai de 1 a 4).
- Em `Age`, os valores acima de 35 anos sao pessoas mais velhas, plausiveis na populacao estudada.
- A maior altura (1,98 m) e o maior peso (173 kg, da classe Obesity_Type_III) sao plausiveis para adultos.

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

Ou seja, o K-Means encontrou perfis de estilo de vida e de corpo, que é o que as 8 variáveis descrevem com peso igual, enquanto as classes reais foram definidas a partir de apenas duas delas (peso e altura, via IMC).

#### Granularidade das classes

As classes foram criadas a partir do IMC (segundo a documentacao do dataset, com base nas faixas da OMS e da normativa mexicana), mas nos dados elas nao funcionam como cortes limpos de uma unica variavel. A tabela de IMC por classe (secao 3.3 do notebook `kmeans_metricas.ipynb`) mostra que as faixas de classes vizinhas se sobrepoem, por exemplo sobrepeso I vai de 22,8 a 28,8 e sobrepeso II de 25,7 a 30,4, e o IMC minimo de sobrepeso I (22,8) fica dentro da faixa de peso normal (18,5 a 24,9). Uma explicacao provavel e que cerca de 77% dos registros foram gerados sinteticamente (SMOTE), por interpolacao entre registros, o que pode criar combinacoes de peso e altura fora da faixa da propria classe. Com isso, nem o IMC sozinho separa perfeitamente as classes vizinhas, e o K-Means tem ainda menos chance, porque as outras 6 variaveis, padronizadas com o mesmo peso, diluem a informacao de peso e altura. Os dados parecem sustentar uma divisao mais grosseira (abaixo do peso ou normal, sobrepeso, obesidade e obesidade severa) do que as 7 classes, o que tambem esta de acordo com o cotovelo sem dobra nitida.

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

**Valores ausentes.** Tres colunas tem ausencias, `workclass` (2.799, 5,73%), `occupation` (2.809, 5,75%) e `native-country` (857, 1,75%). No total, 3.620 linhas (7,41%) tem ao menos um ausente.

**Mecanismo de ausencia.** Em `workclass` e `occupation`, os ausentes ocorrem juntos (as 2.799 linhas sem `workclass` tambem nao tem `occupation`) e nao sao aleatorios. Essas linhas tem mais pessoas com ate 25 anos (38,3% contra 18,6%) e com 65 anos ou mais (17,9% contra 3,4%), jornada mediana menor (36 horas contra 40) e muito menos renda alta (9,5% contra 24,8%). Como a ausencia depende de variaveis observadas, como idade e jornada, classificamos o mecanismo como MAR (ausente de forma aleatoria condicionada aos dados observados). O perfil sugere pessoas fora do mercado formal de trabalho, como estudantes e aposentados. Nao da para descartar totalmente MNAR, porque o motivo de nao informar a ocupacao pode estar ligado a propria ocupacao, e isso nao e testavel com os dados. As 10 linhas a mais de `occupation` ausente sao pessoas com `workclass` igual a Never-worked. Quem nunca trabalhou nao tem ocupacao para informar, entao nesse caso a ausencia e estrutural (o valor nao existe) e nao um dado perdido. Em `native-country`, as linhas com ausente tem perfil muito parecido com as demais (idade e jornada medianas iguais, 37 anos e 40 horas, e taxa de renda alta de 25,7% contra 23,9%), o que e compativel com MCAR (ausente completamente ao acaso), ao menos em relacao as variaveis observadas.

*Tratamento adotado.* Nao removemos linhas. Recodificamos os ausentes de `workclass`, `occupation` e `native-country` como a categoria "Desconhecido". Com mecanismo MAR, excluir essas linhas enviesaria a analise, porque retiraria justamente mais jovens, mais idosos e pessoas com menos renda, deixando a base concentrada em empregos formais. A categoria propria preserva os 7,4% de linhas afetadas e mantem visivel um grupo com perfil de renda diferente. Em `native-country`, como a ausencia parece aleatoria e e pequena (1,75%), a mesma recodificacao nao introduz vies relevante.

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

#### Raciocinio do storytelling

**Publico.** A comunicacao e voltada para a equipe de planejamento educacional e empregabilidade definida acima. Sao pessoas que decidem onde investir em programas de formacao e entendem bem de niveis de ensino, mas nao fazem parte do time tecnico. Por isso os graficos usam os nomes dos niveis de ensino em portugues no lugar dos codigos numericos, os explanatorios tem titulos que ja dizem a conclusao e poucos elementos alem dos dados.

**O que a exploracao mostrou.**
- A base e desbalanceada (76,1% ate US$ 50 mil), entao as comparacoes precisam ser feitas por taxa e nao por contagem.
- Entre todas as variaveis, a escolaridade e a que mais separa a renda. A taxa de renda alta vai de 1,2% na educacao infantil a 74% na escola profissional.
- Olhando os niveis em ordem, a taxa fica abaixo de 8% ate a 12a serie, sobe para 16% no ensino medio completo e da um salto na graduacao (41%). A relacao nao e uma subida gradual, ela tem um ponto de virada.
- Idade, ocupacao, estado civil e sexo tambem se associam a renda, mas nenhuma delas tem uma amplitude tao grande quanto a escolaridade.
- As horas trabalhadas tem a mesma mediana nas duas faixas de renda (40 horas). A diferenca aparece na cauda de jornadas longas, e o cruzamento com a escolaridade mostra que a jornada aumenta a taxa dentro de cada nivel, mas nao compensa um nivel baixo.

**A historia.** Na base Adult, concluir a graduacao e o ponto de virada da renda. Com graduacao ou mais, 48,1% das pessoas ganham acima de US$ 50 mil, contra 16,0% nos niveis abaixo. Trabalhar mais horas ajuda, mas nao substitui a escolaridade, ja que quem tem ensino medio completo e trabalha 51 horas ou mais (28%) ainda fica abaixo de quem tem graduacao e trabalha 40 horas (37%).

**Por que essa mensagem e a mais relevante para esse publico.** A equipe precisa decidir em que etapa da formacao concentrar esforcos. A mensagem aponta onde a diferenca e maior (a conclusao da graduacao) e evita uma leitura comum e enganosa, a de que jornada longa resolve a renda. Como os dados sao descritivos, deixamos claro nos graficos e no texto que se trata de associacao e nao de causa, porque idade, ocupacao e sexo tambem variam junto com a escolaridade.

**Da exploratoria para a explanatoria.** Na exploracao, o grafico de renda por escolaridade (notebook da EDA) mostrava todas as barras na mesma cor, ordenadas pela taxa, com o tamanho de cada grupo e uma linha de media. Na versao explanatoria (grafico 5) mudamos quatro coisas. Colocamos os niveis na ordem de ensino, para que a posicao mostre onde a taxa muda. Usamos cor so nos niveis de graduacao ou mais. Trocamos o titulo descritivo por um titulo que ja diz a conclusao. E retiramos a grade, mantendo apenas o valor ao lado de cada barra. No mapa de calor (grafico 6), trocamos os codigos de escolaridade pelos nomes dos niveis, fixamos a escala de cor de 0 a 100% e escondemos as celulas com menos de 30 pessoas, que antes apareciam com 0% ou valores extremos e podiam enganar.

**Atributos pre atentivos usados.**
- Cor. Vermelho apenas nos niveis de graduacao ou mais e cinza azulado nos demais, para o olho ir direto ao grupo que carrega a mensagem. O corte coincide com os niveis que passam de 40%, entao a cor marca ao mesmo tempo um nivel de ensino e um patamar de renda. O vermelho tambem e a cor da faixa acima de US$ 50 mil em todos os outros graficos, o que mantem o significado da cor no dashboard inteiro.
- Posicao. As barras seguem a ordem dos niveis de ensino e o eixo comeca em zero, entao o salto na graduacao aparece como uma quebra visivel no comprimento das barras.
- Intensidade. No mapa de calor, uma unica escala de amarelo a vermelho representa a taxa, e a cor mais forte fica no canto de maior escolaridade e maior jornada.
- Texto. Os titulos dos graficos explanatorios dizem a conclusao, e os valores aparecem ao lado das barras e dentro das celulas, para que a leitura nao dependa do eixo.

Nao usamos graficos de pizza nem de radar, porque as comparacoes sao entre muitas categorias ordenadas, e barras e mapas de calor permitem comparar comprimentos e posicoes com mais precisao.

#### Notas analiticas das visualizacoes

As visualizacoes 1 a 6 estao em `out/parte_especifica/visualizacoes/` (geradas por `src/parte_especifica/visualizacoes.py`) e aparecem tambem no dashboard, onde cada grafico tem a sua nota analitica. O dashboard tem ainda dois graficos de apoio (estado civil e jornada), com notas proprias no fim desta secao. Os numeros se referem a base completa, sem filtros.

**1. Distribuicao da faixa de renda (exploratoria)**

- **O que mostra.** Quantidade e percentual de pessoas em cada faixa de renda anual.
- **Insight.** A base e desbalanceada, com 37.155 pessoas (76,1%) ate US$ 50 mil e 11.687 (23,9%) acima. Por isso os demais graficos comparam taxas e distribuicoes em percentual, e nao contagens absolutas.
- **Por que este grafico.** Barras comparam duas categorias pelo comprimento, e o rotulo com numero e percentual evita depender da leitura do eixo.

**2. Distribuicao de idade por faixa de renda (exploratoria)**

- **O que mostra.** Distribuicao da idade dentro de cada faixa de renda, em percentual do proprio grupo.
- **Insight.** Quem ganha acima de US$ 50 mil e mais velho (mediana de 43 anos, contra 34). A taxa de renda alta e quase nula ate 25 anos (1,8%) e chega ao maximo entre 46 e 55 anos (39,2%). Mesmo assim as duas distribuicoes se sobrepoem bastante, entao a idade sozinha nao separa as faixas.
- **Por que este grafico.** O histograma mostra forma e sobreposicao de uma variavel numerica, e a normalizacao dentro de cada grupo corrige o desbalanceamento da base.

**3. Nivel de escolaridade por faixa de renda (exploratoria)**

- **O que mostra.** Mediana, quartis e extremos do nivel de escolaridade em cada faixa de renda.
- **Insight.** Entre quem ganha ate US$ 50 mil, metade parou no ensino medio completo ou antes. Entre quem ganha acima, a mediana sobe para tecnologo academico e pelo menos um quarto tem graduacao ou mais. A escolaridade e a variavel que mais desloca a distribuicao entre as duas faixas.
- **Por que este grafico.** O boxplot resume e compara a distribuicao de uma variavel ordenada entre dois grupos de forma compacta.

**4. Taxa de renda acima de US$ 50 mil por ocupacao (exploratoria)**

- **O que mostra.** Taxa de renda acima de US$ 50 mil em cada ocupacao com pelo menos 100 pessoas.
- **Insight.** A taxa vai de 1,2% no servico domestico e 4,1% em outros servicos ate 45,1% em profissional especializado e 47,8% em gerencia e direcao. Pessoas sem ocupacao informada ficam em 9,4%. A ocupacao tambem separa bem a renda, entao parte da diferenca vista por escolaridade pode passar por ela.
- **Por que este grafico.** Barras horizontais acomodam nomes longos e, ordenadas pela taxa, facilitam achar os extremos.

**5. Taxa de renda acima de US$ 50 mil por escolaridade (explanatoria)**

- **O que mostra.** Taxa de renda acima de US$ 50 mil em cada nivel de escolaridade, na ordem dos niveis.
- **Insight.** Ate a 12a serie a taxa fica abaixo de 8% (5,7% no conjunto), sobe para 16% no ensino medio completo e da um salto na graduacao (41%), chegando a 55% no mestrado e a 73% e 74% no doutorado e na escola profissional. Quem tem graduacao ou mais tem taxa de 48,1%, tres vezes a dos demais (16,0%). Este e o grafico que responde diretamente a pergunta de pesquisa.
- **Por que este grafico.** Com as barras na ordem dos niveis, a posicao mostra em que ponto a taxa muda, e a cor destaca so os niveis de graduacao ou mais, que sao exatamente os que passam de 40%.

**6. Escolaridade, jornada semanal e renda (explanatoria)**

- **O que mostra.** Taxa de renda acima de US$ 50 mil para cada combinacao de escolaridade e faixa de horas semanais. Celulas com menos de 30 pessoas ficam em branco.
- **Insight.** De forma geral, a taxa sobe com a jornada ate a faixa de 41 a 50 horas e depois praticamente para de subir. A escolaridade pesa mais que a jornada. Quem tem ensino medio completo e trabalha 51 horas ou mais tem 28% de renda alta, menos do que quem tem graduacao e trabalha 40 horas (37%). Ou seja, jornada longa nao compensa escolaridade baixa.
- **Por que este grafico.** O mapa de calor cruza duas variaveis categorizadas e mostra a taxa pela intensidade da cor. Esconder as celulas pequenas evita que percentuais instaveis chamem atencao.

**Apoio A. Taxa de renda acima de US$ 50 mil por estado civil (dashboard)**

- **O que mostra.** Taxa de renda acima de US$ 50 mil por estado civil, para grupos com pelo menos 100 pessoas.
- **Insight.** Casados no civil tem 44,6% de renda alta, contra 4,5% de quem nunca casou e 10,1% dos divorciados. Parte dessa diferenca vem da idade, ja que quem nunca casou e bem mais jovem (mediana de 25 anos, contra 42 dos casados no civil).
- **Por que este grafico.** Mesmo formato do grafico de ocupacao, para facilitar a comparacao entre os dois.

**Apoio B. Distribuicao da jornada semanal por faixa de renda (dashboard)**

- **O que mostra.** Distribuicao das horas trabalhadas por semana em cada faixa de renda, em percentual do proprio grupo.
- **Insight.** As duas faixas tem mediana de 40 horas, mas 49,1% de quem ganha acima de US$ 50 mil trabalha mais de 40 horas, contra 23,2% de quem ganha ate esse valor. A diferenca esta na cauda de jornadas longas.
- **Por que este grafico.** O histograma normalizado por grupo mostra onde as distribuicoes se separam sem o efeito do desbalanceamento.

#### Resposta a pergunta de pesquisa

Na base Adult, a escolaridade se associa fortemente a proporcao de pessoas com renda anual acima de US$ 50 mil, e essa associacao tem um ponto de virada na graduacao. A taxa fica abaixo de 8% ate a 12a serie, chega a 16% no ensino medio completo e sobe para 41% na graduacao, 55% no mestrado e 73% a 74% no doutorado e na escola profissional. Quem tem graduacao ou mais tem taxa de 48,1%, tres vezes a dos demais niveis (16,0%). As horas trabalhadas contextualizam essa relacao. Dentro de cada nivel, a taxa sobe com a jornada ate cerca de 41 a 50 horas, mas a jornada nao compensa a escolaridade, ja que ensino medio completo com 51 horas ou mais (28%) ainda fica abaixo de graduacao com 40 horas (37%). Esses resultados descrevem associacoes na amostra e nao demonstram causa, porque idade, ocupacao, estado civil e sexo variam junto com a escolaridade e a jornada.

### Dashboard

O dashboard e executado com

    streamlit run src/parte_especifica/dashboard.py

Ele tem duas paginas. A pagina da Parte Especifica reune os indicadores da amostra filtrada e cinco abas. Visao geral (graficos 1 e 2), Exploracao (graficos 3 e 4 e os graficos de apoio de estado civil e jornada), Pergunta de pesquisa (graficos 5 e 6), Explorar duas variaveis e Dados. Os filtros de sexo, tipo de trabalho, idade e horas por semana atualizam todos os graficos e indicadores da pagina, inclusive o titulo do grafico 5, que recalcula as taxas do recorte. Cada grafico tem um botao com a sua nota analitica. Na aba Explorar duas variaveis, o usuario escolhe quaisquer duas variaveis e o grafico se adapta ao tipo delas (mapa de densidade para duas numericas, boxplot para numerica com categorica e barras empilhadas em 100% para duas categoricas), com opcao de separar por faixa de renda. A aba Dados permite exportar o recorte filtrado em CSV.

A segunda pagina e dedicada a Parte Comum. Ela mostra o Metodo do Cotovelo com as duas passadas marcadas, um controle para escolher k de 2 a 10 com os clusters e as classes reais lado a lado na mesma projecao PCA, a matriz de confusao e as metricas do k escolhido, e uma animacao da transicao entre a Passada 1 (k = 4) e a Passada 2 (k = 7).

## Uso de IA

Registrar os usos permitidos, identificar os trechos de código apoiados por IA e anexar a declaração assinada. Declaração: [Clique aqui](docs\DECLARACAO_IA.md)

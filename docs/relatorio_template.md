# Relatório — Projeto Final de AVD

## Integrantes e matriz de contribuição

| Integrante | Contribuições no projeto |
|---|---|
| João Pedro Aguiar Morais | Parte Comum: EDA, padronização dos dados, agrupamento com K-Means e análise de métricas. |
| Galileu Calaça Menezes de Moraes | Parte Comum: mapeamento dos clusters para a classe majoritária, matrizes de confusão, cálculo de acurácia, precisão e recall, verificação da coluna Sobrepeso na matriz das macro-classes (mapeamento um-para-um e análise do meio de transporte) e discussão crítica. Atualização da página da Parte Comum no dashboard. |
| Caio Guimarães Rocha | Parte Específica: implementação das visualizações, organização das notas analíticas e desenvolvimento do dashboard interativo em Streamlit. |
| Mateus de Almeida Ribeiro | Parte Específica e organização do projeto: revisão da Parte Específica, organização da estrutura do repositório e conferência de que todas as entregas atendem aos requisitos do projeto. |

## Parte Comum

### Dataset e preparação

**Fonte.** UCI Machine Learning Repository, *Estimation of Obesity Levels Based On Eating Habits and Physical Condition* (ID 544), arquivo `ObesityDataSet_raw_and_data_sinthetic.csv`. São 2.111 instâncias e 17 atributos: 8 numéricos, 8 categóricos e a variável alvo `NObeyesdad`, com 7 classes de nível de obesidade. Não há valores ausentes.

**Limpeza.** Havia 24 linhas duplicadas, que foram removidas, restando 2.087 linhas. Decidimos remover as duplicatas devido à baixa probabilidade de duas pessoas diferentes responderem exatamente igual a 17 perguntas, o que pode configurar envios duplicados de formulário. Além disso, como o número de linhas duplicadas é pequeno, não perdemos volume relevante.

**Padronização.** Como o K-Means não pode ter acesso aos rótulos reais durante o agrupamento, a coluna `NObeyesdad` foi guardada separada (usada apenas na avaliação e nas métricas) e transformamos as variáveis categóricas em números: as binárias (`Gender`, `family_history_with_overweight`, `FAVC`, `SMOKE` e `SCC`) em 0 e 1, as ordinais `CAEC` e `CALC` em 0 a 3, preservando a ordem de frequência, e a nominal `MTRANS` com One-Hot (uma coluna 0/1 por meio de transporte, porque não há ordem entre eles). Em seguida aplicamos o `StandardScaler` do `scikit-learn` nas 20 variáveis resultantes (as 8 numéricas e as 12 colunas vindas das categóricas).

**Por que incluir as categóricas.** Usamos todas as variáveis do dataset, e não só as numéricas, para que o agrupamento considere também hábitos e histórico (histórico familiar, consumo de comida calórica, álcool e transporte), que a EDA mostrou estarem associados à classe. O custo dessa escolha é o efeito do One-Hot descrito abaixo.

Essa etapa é necessária porque o K-Means forma os grupos calculando a distância euclidiana entre os registros e os centroides. No dataset *Obesity*, as variáveis estão em escalas muito diferentes: por exemplo, `Weight` varia de 39 a 173, enquanto `NCP` varia de 1 a 4 e as colunas binárias valem só 0 ou 1. Sem padronizar os dados, as variáveis de maior escala dominariam o cálculo do K-Means, enquanto as de menor escala teriam peso irrelevante.

Ao aplicar o `StandardScaler`, cada uma das 20 colunas passa a ter média igual a 0 e desvio-padrão igual a 1, de modo que nenhuma coluna domina a distância só por estar numa escala maior.

A padronização iguala o peso de cada **coluna**, não de cada variável original. Como `MTRANS` virou 5 colunas no One-Hot, o meio de transporte entra na distância com o peso de cerca de 5 variáveis. Além disso, nas colunas binárias de categorias raras (por exemplo `MTRANS_Bike`, com 7 pessoas), quem tem a categoria fica com um valor padronizado muito alto (até 17 desvios-padrão), o que afasta essas pessoas de todas as outras. Esse efeito aparece nos resultados do K-Means e está discutido na Discussão crítica.

### EDA

As figuras e tabelas desta secao estao no notebook `notebooks/parte_comum/eda.ipynb`.

Nos gráficos, as classes aparecem sempre na ordem do IMC e com nomes em português (Abaixo do peso, Peso normal, Sobrepeso I e II, Obesidade I, II e III), com uma escala de cor do azul ao vermelho. As categorias ordinais `CAEC` e `CALC` seguem a ordem natural (no, Sometimes, Frequently, Always). No texto mantemos os códigos originais da coluna `NObeyesdad`, entre crases.

**1. Estrutura.** O dataset tem 2.111 linhas e 17 colunas, sendo 8 numericas (`Age`, `Height`, `Weight`, `FCVC`, `NCP`, `CH2O`, `FAF`, `TUE`) e 9 categoricas, incluindo a classe `NObeyesdad`. Nao ha valores ausentes, e as 24 linhas duplicadas foram removidas (ver Dataset e preparacao). Na qualidade dos dados, `FCVC`, `NCP`, `CH2O`, `FAF` e `TUE` vem de perguntas com respostas inteiras, mas entre 30,7% e 61,8% dos valores sao fracionarios. Isso e consistente com a informacao do UCI de que cerca de 77% dos registros foram gerados sinteticamente (SMOTE), por interpolacao. Mantivemos essas escalas como numericas, lembrando que os valores intermediarios nao sao respostas reais.

**2. Distribuicoes.**
- `Age` e concentrada em jovens (metade entre 19,9 e 26 anos, mediana 22,85) e tem cauda longa a direita ate 61 anos.
- `Height` e aproximadamente simetrica em torno de 1,70 m, e `Weight` vai de 39 a 173 kg sem um unico pico, o que combina com classes que vao de abaixo do peso ate obesidade tipo III.
- `FCVC`, `CH2O`, `FAF` e `TUE` tem picos nos valores inteiros e valores espalhados entre eles. `NCP` e muito concentrada em 3 refeicoes (cerca de 70% dos registros).
- Essas cinco variáveis vêm de perguntas com escala ordinal, mas os valores fracionários gerados pelo SMOTE fazem com que se comportem como numéricas contínuas. Por isso usamos histogramas e boxplots para elas, e é assim que entram no K-Means. Os picos nos valores inteiros correspondem às respostas reais do questionário.
- Varias categoricas sao muito desbalanceadas (`SMOKE` 97,9% nao, `SCC` 95,4% nao, `FAVC` 88,4% sim, historico familiar 82,5% sim, `CAEC` 84,4% Sometimes), e algumas categorias quase nao tem casos (`CALC` Always com 1 registro, `MTRANS` Bike com 7 e Motorbike com 11).
- `Gender` (50,4% homens) e as 7 classes (entre 12,8% e 16,8% cada) sao equilibrados, o que e pouco comum em dados reais e e mais um sinal do balanceamento sintetico.

**3. Relacoes.**
- O teste de Shapiro-Wilk rejeitou a normalidade das 8 variáveis numéricas (p-valor menor que 0,05 em todas), então usamos a correlação de Spearman, que trabalha com a ordem dos valores e não supõe normalidade nem relação linear. As correlações são fracas. A maior é entre `Height` e `Weight` (0,46), seguida de `Age` e `Weight` (0,35), `Height` e `FAF` (0,33) e `Age` e `TUE` (-0,31). Nenhum par passa de 0,5, então não há redundância forte entre as variáveis.
- Com a classe, `Weight` cresce de forma ordenada (media de 50,0 kg em Insufficient_Weight ate 120,9 kg em Obesity_Type_III), como esperado para classes criadas a partir do IMC. `Height` so se destaca em Obesity_Type_II (media de 1,77 m), `Age` e maior em Overweight_Level_II e Obesity_Type_II, e `FAF` cai de forma geral das classes mais leves para as mais pesadas.
- Em Obesity_Type_III, `FCVC` e `NCP` valem 3 para todos os registros, o que nao e esperado em dados reais e provavelmente vem da geracao sintetica.
- Para os cruzamentos entre as variáveis categóricas e a classe, que são duas variáveis qualitativas, usamos barras empilhadas em 100%: cada barra é uma categoria e mostra como as pessoas dela se dividem entre as 7 classes, com o número de pessoas ao lado para indicar categorias pequenas.
- Nas categoricas, `Gender` tem a relacao mais forte. Obesity_Type_II e quase so de homens (28% dos homens contra 0,2% das mulheres) e Obesity_Type_III quase so de mulheres (31,2% das mulheres contra 0,1% dos homens), entao nessas classes sexo e grau de obesidade ficam misturados.
- Quem nao tem historico familiar de sobrepeso esta concentrado em Insufficient_Weight (38,9%) e Normal_Weight (35,6%) e nao aparece em Obesity_Type_III. Quem come entre refeicoes com frequencia esta mais em Insufficient_Weight (49,6%), e quem anda a pe esta mais em Normal_Weight (56,4%), mas esta ultima categoria tem poucos registros.

**4. Outliers.** Pelo IQR (1,5 vez), `NCP` teve 577 registros sinalizados (27,65%), `Age` 167 (8,00%) e `Height` e `Weight` 1 cada. Mantivemos todos os registros.
- Em `NCP`, cerca de 70% responderam 3 refeicoes, entao os quartis ficam muito proximos (2,70 e 3,00), o IQR e de 0,30 e os limites ficam entre 2,24 e 3,45. Quem respondeu 1, 2 ou 4 refeicoes vira outlier mesmo sendo uma resposta valida (a pergunta vai de 1 a 4).
- Em `Age`, os valores acima de 35 anos sao pessoas mais velhas, plausiveis na populacao estudada.
- A maior altura (1,98 m) e o maior peso (173 kg, da classe Obesity_Type_III) sao plausiveis para adultos.

### K-Means e métricas

Rodamos o K-Means (`random_state=42`, `n_init=10`) sobre 20 variáveis padronizadas com `StandardScaler`: as 8 numéricas e as categóricas transformadas (binárias `yes`/`no` e `Gender` em 0/1, `CAEC` e `CALC` como ordinais de 0 a 3, e `MTRANS` com One-Hot). Foram duas passadas: k = 4, escolhido pelo Método do Cotovelo, e k = 7, o número real de classes.

**Escolha de k na Passada 1.** Rodamos o K-Means para k de 2 a 10 e registramos a inércia (soma das distâncias ao quadrado de cada ponto ao centro do seu cluster). A curva não tem um cotovelo nítido: a inércia cai 9% de k = 2 para k = 3, 7% de 3 para 4 e, a partir daí, entre 6% e 8% a cada novo cluster. Ou seja, a partir de k = 4 cada cluster a mais traz um ganho parecido, sem um ponto em que a queda pare de forma clara. Escolhemos k = 4 por ser o ponto em que as quedas se estabilizam e por manter um número pequeno de grupos, que ainda dá para interpretar. Como o cotovelo não é claro, essa escolha tem uma parte subjetiva (ver Limitações).

**Visualização dos grupos.** Para visualizar os clusters das duas passadas, projetamos as 20 variáveis em 2 dimensões com PCA e colorimos cada ponto pelo seu cluster (figuras `clusters_livre.png` e `clusters_fixo.png`). As duas componentes explicam só cerca de 25% da variância (13,8% e 11,6%), então grupos que estão separados nas 20 dimensões podem aparecer sobrepostos no gráfico. O PCA foi usado apenas para desenhar e não interfere no agrupamento. Como os 2.087 pontos se sobrepõem num único gráfico, também geramos uma versão com um painel por cluster (`clusters_livre_paineis.png` e `clusters_fixo_paineis.png`), em que cada painel destaca um cluster sobre os demais pontos em cinza. O dashboard tem a mesma opção.

O K-Means não vê o rótulo `NObeyesdad`. Para avaliar, cada cluster foi mapeado para a classe real majoritária dentro dele, e todas as pessoas do cluster recebem esse rótulo previsto. A matriz de confusão compara o rótulo previsto com a classe real. Na Passada 1 a matriz é 7×4 (só 4 rótulos possíveis) e na Passada 2 é 7×7. Acurácia, precisão e recall por classe foram calculados a partir da matriz (notebook `kmeans_metricas.ipynb`, figuras em `out/parte_comum/kmeans/`).

Dois detalhes da avaliação:
- "Classe majoritária" significa a classe **mais frequente** dentro do cluster, não necessariamente mais da metade. No cluster 1 da Passada 1, por exemplo, a classe que dá nome ao cluster (`Obesity_Type_I`) tem 24,8% das pessoas.
- Quando nenhum cluster recebe o nome de uma classe, a precisão dela é indefinida (0 dividido por 0, porque ninguém foi previsto como aquela classe). Nesses casos registramos 0, o que puxa a precisão média (macro) para baixo. Isso explica parte da diferença de precisão média entre as passadas: a Passada 1 tem 3 classes nunca previstas e a Passada 2 tem 2.

| Passada | k | Acurácia | Precisão macro | Recall macro | Classes representadas |
|---|---|---|---|---|---|
| 1 — k livre | 4 | 0,317 | 0,215 | 0,309 | 4/7 |
| 2 — k fixo | 7 | 0,306 | 0,256 | 0,299 | 5/7 |

Baseline (prever sempre a classe mais frequente): acurácia 0,168.

| Classe | Recall P1 | Recall P2 | Precisão P1 | Precisão P2 |
|---|---|---|---|---|
| Insufficient_Weight | 0,704 | 0,528 | 0,397 | 0,411 |
| Normal_Weight | 0,145 | 0,145 | 0,562 | 0,562 |
| Overweight_Level_I | 0,000 | 0,000 | 0,000 | 0,000 |
| Overweight_Level_II | 0,000 | 0,000 | 0,000 | 0,000 |
| Obesity_Type_I | 0,313 | 0,313 | 0,248 | 0,249 |
| Obesity_Type_II | 0,000 | 0,498 | 0,000 | 0,226 |
| Obesity_Type_III | 0,997 | 0,611 | 0,294 | 0,344 |

Na Passada 1, cada cluster recebeu um rótulo diferente (`Obesity_Type_III`, `Obesity_Type_I`, `Insufficient_Weight` e `Normal_Weight`), e a classe majoritária ocupa de 24,8% a 56,2% de cada cluster. Na Passada 2, três clusters foram mapeados para `Normal_Weight`, de modo que `Overweight_Level_I` e `Overweight_Level_II` não são previstas.

**Análise complementar com 4 macro-classes.** Agrupando as 7 classes em Abaixo do Peso, Normal, Sobrepeso (níveis I e II) e Obesidade (tipos I, II e III), o K-Means com k = 4 chega a acurácia 0,568 (baseline 0,466). Pelo mapeamento por maioria, porém, dois clusters recebem o rótulo Obesidade e a coluna Sobrepeso da matriz fica zerada. Verificamos que isso não é erro de código: as pessoas com sobrepeso estão nos mesmos clusters que as com obesidade, que é a maioria (46,6% do dataset). Cruzando os clusters com `MTRANS`, vimos que eles foram formados principalmente pelo meio de transporte: na Passada 1, um cluster é 100% transporte público, outro 100% carro e outro reúne a pé, bicicleta e moto. Com um mapeamento um-para-um (algoritmo húngaro, cada cluster recebe uma macro-classe diferente, escolhida para maximizar o total de acertos; só é possível aqui porque o número de clusters, 4, é igual ao de macro-classes), Sobrepeso passa a ser prevista (recall 0,281, precisão 0,359) e a acurácia fica em 0,546.

| Macro-classe | Recall (maioria) | Recall (um-para-um) | Precisão (maioria) | Precisão (um-para-um) |
|---|---|---|---|---|
| Abaixo do Peso | 0,704 | 0,704 | 0,397 | 0,397 |
| Normal | 0,145 | 0,145 | 0,562 | 0,562 |
| Sobrepeso | 0,000 | 0,281 | 0,000 | 0,359 |
| Obesidade | 0,985 | 0,773 | 0,621 | 0,684 |

### Discussão crítica

#### Qual passada gerou grupos mais coerentes?

As duas passadas ficaram muito próximas, e nenhuma reproduz bem as 7 classes. A Passada 1 (k = 4) teve acurácia um pouco maior (0,317 contra 0,306) e recall médio um pouco maior (0,309 contra 0,299); a Passada 2 (k = 7) teve precisão média maior (0,256 contra 0,215) e representa 5 das 7 classes, contra 4. As duas superam o baseline de 0,168 (prever sempre a classe mais frequente), então os clusters carregam alguma informação sobre o nível de obesidade, mas pouca: cerca de 7 em cada 10 pessoas caem num cluster cuja classe majoritária não é a sua.

Consideramos a Passada 1 a mais coerente. Com quase o mesmo desempenho, ela usa menos grupos, e seus 4 clusters têm tamanhos razoáveis. Na Passada 2, os 3 clusters a mais não foram usados para separar níveis de obesidade: três deles (0, 4 e 6) têm só 55, 11 e 7 pessoas e são formados, respectivamente, só por quem anda a pé, de moto e de bicicleta (seção 3.5 do notebook), e os três receberam o rótulo `Normal_Weight`. O único ganho real da Passada 2 é separar `Obesity_Type_II` de `Obesity_Type_III` (recall de `Obesity_Type_II` vai de 0 para 0,498), e essa separação veio do sexo, como mostrado abaixo.

#### Por que algumas classes nunca são previstas?

No mapeamento pela classe majoritária, cada cluster recebe o nome da classe real mais frequente dentro dele, e vários clusters podem receber o mesmo nome. Na Passada 2, três clusters viraram `Normal_Weight`, e sobram só 5 rótulos distintos; `Overweight_Level_I` e `Overweight_Level_II` nunca são previstas (recall 0 nas duas passadas). Essas pessoas estão espalhadas: na Passada 2, `Overweight_Level_II` aparece com 71, 94 e 106 registros nos clusters 1, 2 e 3, e em nenhum deles é maioria. As faixas de sobrepeso ficam no meio da escala de IMC e se sobrepõem às classes vizinhas.

O mesmo acontece na análise com 4 macro-classes (seção 3.4 do notebook): os clusters 0 e 1 têm maioria de Obesidade (Obesidade é 46,6% do dataset), os dois recebem esse rótulo e a coluna "Sobrepeso" da matriz fica zerada. Com o mapeamento um-para-um (seção 3.5 do notebook), Sobrepeso passa a aparecer (recall 0,28), mas a acurácia cai de 0,568 para 0,546 e a maior parte das pessoas com sobrepeso continua no cluster de Obesidade. Ou seja, o mapeamento explica a coluna zerada, mas a causa de fundo é que os clusters não separam sobrepeso de obesidade.

#### O que o K-Means realmente agrupou

- *Meio de transporte:* é o eixo principal. Na Passada 1, o cluster 0 é 100% transporte público, o cluster 1 é 100% carro e o cluster 3 reúne a pé, bicicleta e moto. Na Passada 2 cada cluster tem praticamente um único meio de transporte. Isso acontece porque, depois do One-Hot e da padronização, `MTRANS` virou 5 colunas, e as categorias raras ganharam valores muito altos (até 17 desvios-padrão em `MTRANS_Bike`), então uma variável pesa como cinco na distância.
- *Sexo/altura:* na Passada 2, os clusters 1 e 3 são ambos de transporte público, mas o cluster 1 tem 83% de mulheres e altura média de 1,64 m, e o cluster 3 tem 21% de mulheres e 1,78 m. O cluster feminino fica com maioria `Obesity_Type_III` e o masculino com `Obesity_Type_II`. Como o IMC é peso dividido pela altura ao quadrado, a separação entre esses níveis veio do sexo, não de um grau maior de obesidade.
- *Histórico familiar e idade:* o cluster 5 da Passada 2, de maioria `Insufficient_Weight`, é o único em que poucos têm histórico familiar de sobrepeso (12%, contra 55% a 100% nos demais), e o cluster 2 (carro) é o mais velho (idade média de 32 anos).

Ou seja, o K-Means encontrou perfis de estilo de vida e de corpo, que é o que as 20 variáveis descrevem com peso igual, enquanto as classes reais foram definidas a partir de apenas duas delas (peso e altura, via IMC).

#### Granularidade das classes

As classes foram criadas a partir do IMC (segundo a documentação do dataset, com base nas faixas da OMS e da normativa mexicana), mas nos dados elas não funcionam como cortes limpos de uma única variável. A tabela de IMC por classe (seção 3.3 do notebook `kmeans_metricas.ipynb`) mostra que as faixas de classes vizinhas se sobrepõem: por exemplo, sobrepeso I vai de 22,8 a 28,8 e sobrepeso II de 25,7 a 30,4, e o IMC mínimo de sobrepeso I (22,8) fica dentro da faixa de peso normal (18,5 a 24,9). Uma explicação provável é que cerca de 77% dos registros foram gerados sinteticamente (SMOTE), por interpolação entre registros, o que pode criar combinações de peso e altura fora da faixa da própria classe. Com isso, nem o IMC sozinho separa perfeitamente as classes vizinhas, e o K-Means tem ainda menos chance, porque as outras 18 variáveis, padronizadas com o mesmo peso, diluem a informação de peso e altura.

O agrupamento em 4 macro-classes confirma que uma divisão mais grosseira combina melhor com os dados: com k = 4, a acurácia sobe para 0,568 (baseline 0,466), contra 0,317 nas 7 classes. Mesmo assim, Normal (recall 0,145) e Sobrepeso continuam mal separados, porque ficam no meio da escala e se misturam com as classes vizinhas.

#### Limitações

- A codificação One-Hot de `MTRANS`, padronizada junto com as outras variáveis, fez o transporte dominar o agrupamento. Uma alternativa seria dar menos peso a essas colunas ou não padronizar as variáveis binárias.
- Cerca de 77% do dataset foi gerado sinteticamente (SMOTE) pelos autores. Isso explica valores fracionários em variáveis que deveriam ser discretas (`FCVC`, `NCP`, `FAF`, `TUE`, `CH2O`) e pode criar padrões artificiais.
- A escolha de k = 4 foi feita pelo cotovelo, que não tem um ponto de inflexão claro.
- O mapeamento pela classe majoritária permite que vários clusters recebam o mesmo rótulo e deixa classes sem representação, o que penaliza as métricas por classe.
- O K-Means assume grupos esféricos e de tamanho parecido, o que não vale aqui: na Passada 2 há clusters de 7 e de 654 pessoas.

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

A EDA está em `notebooks/parte_especifica/eda.ipynb`, e as figuras geradas por ele estão em `out/parte_especifica/figuras/`. As tabelas de apoio estão em `out/parte_especifica/eda/` (geradas por `src/parte_especifica/eda_inicial.py`).

**1. Estrutura.** 48.842 linhas e 15 colunas: 6 numéricas inteiras (`age`, `fnlwgt`, `education-num`, `capital-gain`, `capital-loss`, `hours-per-week`) e 9 categóricas (incluindo `income`). `education` e `education-num` descrevem a mesma informação (16 níveis); usamos apenas uma delas por análise (`education-num` para ordenar os níveis, com os nomes em português nos gráficos). `fnlwgt` é um peso amostral do censo, não uma característica da pessoa, e não foi usado na análise. A classe é desbalanceada: 37.155 (76,1%) `<=50K` e 11.687 (23,9%) `>50K`.

**2. Distribuições.**
- `age`: média 38,6, mediana 37, intervalo 17–90, ligeiramente assimétrica à direita. O valor 90 é um teto da base (186 pessoas com 80 anos ou mais).
- `hours-per-week`: mediana 40 e 46,7% das pessoas trabalham exatamente 40 horas; há caudas em ambos os lados (1.125 com 10 horas ou menos; 528 com 80 ou mais).
- `capital-gain` e `capital-loss`: dominadas por zeros. Só 8,3% têm ganho de capital e 4,7% têm perda; o máximo de ganho (99.999) é um valor de teto e aparece 244 vezes.
- `education-num`: mediana 10 (ensino médio completo e alguma faculdade concentram a maior parte).
- Categóricas: 69,4% trabalham no setor privado, 91,3% nasceram nos EUA, 85,5% são brancos e 66,8% são homens. A amostra é pouco diversa em país de origem e raça, então comparações envolvendo grupos pequenos (por exemplo `Other`, com 406 pessoas) devem ser lidas com cautela.

**3. Relações com a classe.**
- *Idade e horas:* quem ganha `>50K` é mais velho (média 44,3 contra 36,9) e trabalha mais (45,5 contra 38,8 horas por semana), mas as medianas de horas são iguais (40), então a diferença vem da cauda de longas jornadas.
- *Escolaridade:* é a variável categórica mais associada à renda. A proporção de `>50K` vai de 1% a 16% até o ensino médio, sobe para 41% em bacharelado, 55% em mestrado e passa de 72% em doutorado e escola profissional.
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
- O valor 99.999 em `capital-gain` é um código de teto, não um valor exato.

Como a pergunta de pesquisa trata de escolaridade e horas, `capital-gain` e `capital-loss` não entram nas seis visualizações; elas aparecem apenas no explorador de duas variáveis do dashboard, agrupadas em faixas (sem valor, até 5.000, de 5.001 a 10.000 e acima de 10.000), de modo que o teto de 99.999 cai na última faixa. As horas foram agrupadas em faixas (até 20, 21 a 39, 40, 41 a 50 e 51 ou mais) para o gráfico 6, e a escolaridade foi agrupada em 5 grupos (ver Storytelling e visualizações). Por causa do desbalanceamento da classe (76/24), todas as comparações usam a taxa de renda alta dentro de cada grupo, e não contagens.

### Storytelling e visualizações

#### Raciocinio do storytelling

**Publico.** A comunicacao e voltada para a equipe de planejamento educacional e empregabilidade definida acima. Sao pessoas que decidem onde investir em programas de formacao e entendem bem de niveis de ensino, mas nao fazem parte do time tecnico. Por isso os graficos usam nomes de escolaridade em portugues no lugar dos codigos numericos, os explanatorios tem titulos que ja dizem a conclusao e poucos elementos alem dos dados.

**Agrupamento da escolaridade.** A base usa 16 niveis do sistema escolar dos EUA, varios deles com poucas pessoas e sem equivalente direto no Brasil (por exemplo, associate degree e professional school). Para simplificar a leitura, agrupamos os 16 niveis em 5 grupos, mantendo a classificacao americana e indicando isso nos rotulos e nas notas:

| Grupo | Niveis originais | Pessoas | Taxa de renda acima de US$ 50 mil |
|---|---|---|---|
| Ate 8a serie | Preschool a 7th-8th | 1.794 | 5,5% |
| 9a a 12a serie, sem diploma | 9th a 12th | 4.614 | 5,8% |
| Ensino medio completo | HS-grad | 15.784 | 15,9% |
| Faculdade sem diploma ou associate degree | Some-college, Assoc-voc, Assoc-acdm | 14.540 | 20,6% |
| Bacharelado ou titulacao superior | Bachelors, Masters, Prof-school, Doctorate | 12.110 | 48,1% |

Os grupos seguem a hierarquia de ensino. Professional school (titulos profissionais como medicina e direito) entra no ultimo grupo junto com mestrado e doutorado, porque nao forma uma escala linear com eles. O mesmo agrupamento e usado em todos os graficos que mostram escolaridade (3, 5 e 6) e no explorador do dashboard.

**O que a exploracao mostrou.**
- A base e desbalanceada (76,1% ate US$ 50 mil), entao as comparacoes precisam ser feitas por taxa e nao por contagem.
- Entre todas as variaveis, a escolaridade e a que mais separa a renda. Nos 16 niveis originais, a taxa de renda alta vai de 1,2% na educacao infantil a 74% na escola profissional.
- Com os grupos em ordem, a taxa fica perto de 6% ate a 12a serie sem diploma, sobe para 15,9% no ensino medio completo e 20,6% em faculdade ou associate degree, e da um salto para 48,1% em bacharelado ou mais. A relacao nao e uma subida gradual, ela tem um ponto de virada no bacharelado.
- Idade, ocupacao, estado civil e sexo tambem se associam a renda, mas nenhuma delas tem uma amplitude tao grande quanto a escolaridade.
- As horas trabalhadas tem a mesma mediana nas duas faixas de renda (40 horas). A diferenca aparece na cauda de jornadas longas, e o cruzamento com a escolaridade mostra que a jornada aumenta a taxa dentro de cada grupo, mas nao compensa uma escolaridade baixa.

**A historia.** Na base Adult, concluir o bacharelado e o ponto de virada da renda. Com bacharelado ou mais, 48,1% das pessoas ganham acima de US$ 50 mil, contra 16,0% nos grupos abaixo. Trabalhar mais horas ajuda, mas nao substitui a escolaridade, ja que quem tem ensino medio completo e trabalha 51 horas ou mais (27,9%) ainda fica abaixo de quem tem bacharelado ou mais e trabalha 40 horas (42,3%).

**Por que essa mensagem e a mais relevante para esse publico.** A equipe precisa decidir em que etapa da formacao concentrar esforcos. A mensagem aponta onde a diferenca e maior (a conclusao do bacharelado) e evita uma leitura comum e enganosa, a de que jornada longa resolve a renda. Como os dados sao descritivos, deixamos claro nos graficos e no texto que se trata de associacao e nao de causa, porque idade, ocupacao e sexo tambem variam junto com a escolaridade.

**Da exploratoria para a explanatoria.** Na exploracao, o grafico de renda por escolaridade (notebook da EDA) mostrava os 16 niveis na mesma cor, ordenados pela taxa, com o tamanho de cada grupo e uma linha de media. Na versao explanatoria (grafico 5) mudamos cinco coisas. Agrupamos os niveis em 5 grupos, para reduzir o numero de barras. Colocamos os grupos na ordem de ensino, para que a posicao mostre onde a taxa muda. Usamos cor so no grupo de bacharelado ou mais. Trocamos o titulo descritivo por um titulo que ja diz a conclusao. E retiramos a grade, mantendo apenas o valor ao lado de cada barra. No grafico 6, trocamos o mapa de calor com 16 niveis por um grafico de linhas com os 5 grupos: as faixas de horas sao ordenadas, entao a linha mostra a tendencia de cada grupo e a distancia entre eles, sem depender da comparacao de intensidades de cor.

**Atributos pre atentivos usados.**
- Cor. Coral apenas no grupo de bacharelado ou mais e tons de cinza azulado nos demais, para o olho ir direto ao grupo que carrega a mensagem. O coral tambem e a cor da faixa acima de US$ 50 mil nos outros graficos, o que mantem o significado da cor no dashboard inteiro.
- Posicao. As barras seguem a ordem dos grupos de ensino e o eixo comeca em zero, entao o salto no bacharelado aparece como uma quebra visivel no comprimento das barras. No grafico 6, a altura de cada linha mostra a taxa, e a linha coral fica acima de todas as outras em qualquer jornada.
- Espessura. No grafico 6, a linha do bacharelado ou mais e mais grossa que as demais.
- Texto. Os titulos dos graficos explanatorios dizem a conclusao, e os valores aparecem ao lado das barras e no fim de cada linha, para que a leitura nao dependa do eixo.

Nao usamos graficos de pizza nem de radar, porque as comparacoes sao entre categorias ordenadas, e barras e linhas permitem comparar comprimentos e posicoes com mais precisao.

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

**3. Faixa de renda em cada grupo de escolaridade (exploratoria)**

- **O que mostra.** Composicao percentual das faixas de renda dentro de cada grupo de escolaridade (cada barra soma 100%).
- **Insight.** A parcela com renda acima de US$ 50 mil cresce a cada grupo: 5,5% ate a 8a serie, 5,8% da 9a a 12a serie sem diploma, 15,9% no ensino medio completo, 20,6% em faculdade sem diploma ou associate degree e 48,1% em bacharelado ou mais. O maior salto esta entre os dois ultimos grupos, e a escolaridade e a variavel que mais separa as faixas de renda.
- **Por que este grafico.** Escolaridade agrupada e faixa de renda sao duas variaveis qualitativas, entao barras empilhadas em 100% mostram a composicao de cada grupo sem o efeito do desbalanceamento da base. Esse grafico substituiu o boxplot, que tratava a escolaridade como numero.

**4. Taxa de renda acima de US$ 50 mil por ocupacao (exploratoria)**

- **O que mostra.** Taxa de renda acima de US$ 50 mil em cada ocupacao com pelo menos 100 pessoas.
- **Insight.** A taxa vai de 1,2% no servico domestico e 4,1% em outros servicos ate 45,1% em profissional especializado e 47,8% em gerencia e direcao. Pessoas sem ocupacao informada ficam em 9,4%. A ocupacao tambem separa bem a renda, entao parte da diferenca vista por escolaridade pode passar por ela.
- **Por que este grafico.** Barras horizontais acomodam nomes longos e, ordenadas pela taxa, facilitam achar os extremos.

**5. Taxa de renda acima de US$ 50 mil por escolaridade (explanatoria)**

- **O que mostra.** Taxa de renda acima de US$ 50 mil em cada grupo de escolaridade, na ordem dos niveis de ensino.
- **Insight.** Ate a 12a serie sem diploma a taxa fica perto de 6%. Ela sobe para 15,9% no ensino medio completo e 20,6% em faculdade sem diploma ou associate degree, e da um salto para 48,1% em bacharelado ou mais, tres vezes a taxa do conjunto abaixo do bacharelado (16,0%). Este e o grafico que responde diretamente a pergunta de pesquisa.
- **Por que este grafico.** Com as barras na ordem dos niveis, a posicao mostra onde a taxa muda, e a cor destaca so o grupo de bacharelado ou mais, que concentra a diferenca. O titulo ja diz a conclusao.

**6. Escolaridade, jornada semanal e renda (explanatoria)**

- **O que mostra.** Taxa de renda acima de US$ 50 mil em cada faixa de horas semanais, com uma linha para cada grupo de escolaridade. Pontos com menos de 30 pessoas sao omitidos.
- **Insight.** Em todos os grupos a taxa sobe com a jornada ate a faixa de 41 a 50 horas e depois quase nao muda (bacharelado ou mais vai de 60,6% para 62,4%). A escolaridade pesa mais que a jornada: quem tem ensino medio completo e trabalha 51 horas ou mais tem 27,9% de renda alta, menos do que quem tem bacharelado ou mais e trabalha 40 horas (42,3%). Ou seja, jornada longa nao compensa escolaridade baixa.
- **Por que este grafico.** As faixas de horas sao ordenadas, entao linhas mostram a tendencia de cada grupo ao longo da jornada e a distancia entre os grupos ao mesmo tempo. Com 5 grupos, a comparacao fica mais direta do que no mapa de calor usado antes, em que era preciso comparar intensidades de cor.

**Apoio A. Taxa de renda acima de US$ 50 mil por estado civil (dashboard)**

- **O que mostra.** Taxa de renda acima de US$ 50 mil por estado civil, para grupos com pelo menos 100 pessoas.
- **Insight.** Casados no civil tem 44,6% de renda alta, contra 4,5% de quem nunca casou e 10,1% dos divorciados. Parte dessa diferenca vem da idade, ja que quem nunca casou e bem mais jovem (mediana de 25 anos, contra 42 dos casados no civil).
- **Por que este grafico.** Mesmo formato do grafico de ocupacao, para facilitar a comparacao entre os dois.

**Apoio B. Distribuicao da jornada semanal por faixa de renda (dashboard)**

- **O que mostra.** Distribuicao das horas trabalhadas por semana em cada faixa de renda, em percentual do proprio grupo, em paineis separados.
- **Insight.** As duas faixas tem mediana de 40 horas, mas 49,1% de quem ganha acima de US$ 50 mil trabalha mais de 40 horas, contra 23,2% de quem ganha ate esse valor. A diferenca esta na cauda de jornadas longas.
- **Por que este grafico.** Histogramas em paineis separados e com a mesma escala permitem comparar as distribuicoes sem a sobreposicao que havia quando as duas apareciam no mesmo grafico. Os percentuais sao calculados dentro de cada faixa de renda.

#### Resposta a pergunta de pesquisa

Na base Adult, a escolaridade se associa fortemente a proporcao de pessoas com renda anual acima de US$ 50 mil, e essa associacao tem um ponto de virada no bacharelado. A taxa fica perto de 6% ate a 12a serie sem diploma, chega a 15,9% no ensino medio completo e 20,6% em faculdade sem diploma ou associate degree, e sobe para 48,1% em bacharelado ou mais, tres vezes a dos grupos abaixo (16,0%). As horas trabalhadas contextualizam essa relacao. Dentro de cada grupo, a taxa sobe com a jornada ate cerca de 41 a 50 horas e depois se estabiliza, mas a jornada nao compensa a escolaridade, ja que ensino medio completo com 51 horas ou mais (27,9%) ainda fica abaixo de bacharelado ou mais com 40 horas (42,3%). Esses resultados descrevem associacoes na amostra e nao demonstram causa, porque idade, ocupacao, estado civil e sexo variam junto com a escolaridade e a jornada.

### Dashboard

O dashboard e executado com

    streamlit run src/parte_especifica/dashboard.py

Ele tem duas paginas e um tema visual proprio (fundo escuro, azul para a faixa ate US$ 50 mil e coral para a faixa acima). A pagina da Parte Especifica reune os indicadores da amostra filtrada e cinco abas. Visao geral (graficos 1 e 2), Exploracao (graficos 3 e 4 e os graficos de apoio de estado civil e jornada), Pergunta de pesquisa (graficos 5 e 6), Explorar duas variaveis e Dados. Os filtros de sexo, tipo de trabalho, idade e horas por semana atualizam todos os graficos e indicadores da pagina, inclusive o titulo do grafico 5, que recalcula as taxas do recorte. Cada grafico tem um botao com a sua nota analitica. Na aba Explorar duas variaveis, o usuario escolhe quaisquer duas variaveis e ve o cruzamento em barras empilhadas em 100%; as variaveis numericas sao apresentadas em faixas fixas e a escolaridade usa os mesmos 5 grupos dos graficos, com opcao de separar por faixa de renda. A aba Dados permite exportar o recorte filtrado em CSV.

A segunda pagina e dedicada a Parte Comum. Ela mostra o Metodo do Cotovelo com as duas passadas marcadas, um controle para escolher k de 2 a 10 com os clusters e as classes reais lado a lado na mesma projecao PCA (com opcao de um painel por cluster), a matriz de confusao e as metricas do k escolhido, uma animacao da transicao entre a Passada 1 (k = 4) e a Passada 2 (k = 7) e a verificacao com as 4 macro-classes.

## Uso de IA

Registrar os usos permitidos, identificar os trechos de código apoiados por IA e anexar a declaração assinada. Declaração: [Clique aqui](DECLARACAO_IA.md)

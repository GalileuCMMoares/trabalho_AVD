# Visualizações — Parte Específica (Adult)

## Pergunta de pesquisa

**Como a escolaridade se associa à proporção de pessoas com renda anual acima de US$ 50 mil na base Adult, e como as horas trabalhadas ajudam a contextualizar essa associação?**

## Público-alvo

Equipe de planejamento educacional e empregabilidade que precisa de uma visão inicial dos perfis presentes na amostra. O objetivo é identificar padrões descritivos que merecem investigação adicional; os resultados não demonstram causalidade nem devem embasar decisões individuais.

## Conjunto de seis visualizações

| Arquivo | Papel | O que mostra | Insight | Motivo da escolha |
|---|---|---|---|---|
| `01 - Distribuição por Renda` | Exploratória | Quantidade e percentual das duas classes de renda. | A base é desbalanceada: aproximadamente 76% estão em `<=50K` e 24% em `>50K`. Comparações posteriores devem usar taxas, não apenas contagens. | Barras comparam duas categorias com clareza. |
| `02 - Idade por Renda` | Exploratória | Distribuição percentual de idade dentro de cada faixa de renda. | A distribuição de `>50K` tende a se concentrar em idades maiores que a de `<=50K`, embora exista sobreposição. | Histogramas mostram forma, dispersão e sobreposição de uma variável numérica entre grupos. |
| `03 - Escolaridade por Renda` | Exploratória | Mediana, dispersão e extremos de `education-num` para cada classe. | A distribuição de escolaridade de `>50K` fica deslocada para níveis maiores, mas há registros de ambos os grupos em vários níveis. | Boxplots comparam mediana, quartis e extremos de forma compacta. |
| `04 - Renda por ocupação` | Exploratória | Proporção de renda `>50K` por ocupação, excluindo grupos muito pequenos. | As taxas variam entre ocupações, apontando ocupação como variável relevante para aprofundamento. | Barras horizontais acomodam nomes longos e facilitam ordenar categorias. |
| `05 - Pergunta por escolaridade` | Explanatória | Taxa de `>50K` em cada categoria de escolaridade. | Os níveis mais altos de escolaridade apresentam taxas maiores de renda acima de US$ 50 mil na amostra. Esta figura responde diretamente à pergunta de pesquisa. | Barras ordenadas permitem comparar as categorias; a cor evidencia o patamar de 40%. |
| `06 - Escolaridade por Horas` | Explanatória | Taxa de `>50K` para combinações de escolaridade numérica e faixas de horas semanais. | A associação com renda alta é mais visível em combinações de maior escolaridade e jornadas mais longas. O tamanho amostral das células deve ser considerado. | O mapa de calor sintetiza duas dimensões categorizadas e uma medida percentual pela cor. |

As seis figuras são geradas pelo script `src/parte_especifica/visualizacoes.py` (com `pandas`, `matplotlib` e `seaborn`) e ficam em `out/parte_especifica/visualizacoes/`, em formato PNG, com os nomes da coluna Arquivo.
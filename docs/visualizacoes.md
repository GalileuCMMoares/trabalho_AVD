# Visualizações — Parte Específica (Adult)

## Pergunta de pesquisa

**Como a escolaridade se associa à proporção de pessoas com renda anual acima de US$ 50 mil na base Adult, e como as horas trabalhadas ajudam a contextualizar essa associação?**

## Público-alvo

Equipe de planejamento educacional e empregabilidade que precisa de uma visão inicial dos perfis presentes na amostra. O objetivo é identificar padrões descritivos que merecem investigação adicional; os resultados não demonstram causalidade nem devem embasar decisões individuais.

## Conjunto de seis visualizações

| Arquivo | Papel | O que mostra | Insight | Motivo da escolha |
|---|---|---|---|---|
| `01 - Distribuição por Renda` | Exploratória | Quantidade e percentual de pessoas em cada faixa de renda anual. | A base e desbalanceada, com 37.155 pessoas (76,1%) ate US$ 50 mil e 11.687 (23,9%) acima, entao os demais graficos comparam taxas e percentuais, e nao contagens. | Barras comparam duas categorias pelo comprimento, e o rotulo com numero e percentual evita depender do eixo. |
| `02 - Idade por Renda` | Exploratória | Distribuicao da idade dentro de cada faixa de renda, em percentual do proprio grupo. | Quem ganha acima de US$ 50 mil e mais velho (mediana de 43 anos, contra 34), mas as distribuicoes se sobrepoem bastante. | Histograma normalizado por grupo mostra forma e sobreposicao sem o efeito do desbalanceamento. |
| `03 - Escolaridade por Renda` | Exploratória | Mediana, quartis e extremos do nivel de escolaridade em cada faixa de renda, com os nomes dos niveis no eixo. | Entre quem ganha ate US$ 50 mil, metade parou no ensino medio completo ou antes. Entre quem ganha acima, a mediana sobe para tecnologo academico. | Boxplot compara a distribuicao de uma variavel ordenada entre dois grupos de forma compacta. |
| `04 - Renda por ocupação` | Exploratória | Taxa de renda acima de US$ 50 mil por ocupacao, para ocupacoes com pelo menos 100 pessoas. | A taxa vai de 1,2% no servico domestico a 47,8% em gerencia e direcao, entao a ocupacao tambem separa bem a renda. | Barras horizontais acomodam nomes longos e, ordenadas pela taxa, facilitam achar os extremos. |
| `05 - Pergunta por escolaridade` | Explanatória | Taxa de renda acima de US$ 50 mil em cada nivel de escolaridade, na ordem dos niveis. | A taxa fica abaixo de 8% ate a 12a serie e da um salto na graduacao (41%). Com graduacao ou mais, a taxa e de 48,1%, contra 16,0% nos demais. Responde diretamente a pergunta de pesquisa. | A ordem dos niveis mostra onde a taxa muda, e a cor destaca so a graduacao ou mais, que sao os niveis acima de 40%. |
| `06 - Escolaridade por Horas` | Explanatória | Taxa de renda acima de US$ 50 mil por nivel de escolaridade e faixa de horas semanais. Celulas com menos de 30 pessoas ficam em cinza. | A taxa sobe com a jornada ate 41 a 50 horas, mas a escolaridade pesa mais. Ensino medio completo com 51 horas ou mais (28%) fica abaixo de graduacao com 40 horas (37%). | O mapa de calor cruza duas variaveis categorizadas e mostra a taxa pela cor, com escala fixa de 0 a 100%. |

As seis figuras são geradas pelo script `src/parte_especifica/visualizacoes.py` (com `pandas`, `matplotlib` e `seaborn`) e ficam em `out/parte_especifica/visualizacoes/`, em formato PNG, com os nomes da coluna Arquivo. As mesmas seis visualizacoes aparecem no dashboard, cada uma com a sua nota analitica, e as notas completas estao no relatorio.
# Visualizações — Parte Específica (Adult)

## Pergunta de pesquisa

**Como a escolaridade se associa à proporção de pessoas com renda anual acima de US$ 50 mil na base Adult, e como as horas trabalhadas ajudam a contextualizar essa associação?**

## Público-alvo

Equipe de planejamento educacional e empregabilidade que precisa de uma visão inicial dos perfis presentes na amostra. O objetivo é identificar padrões descritivos que merecem investigação adicional; os resultados não demonstram causalidade nem devem embasar decisões individuais.

## Conjunto de seis visualizações

| Arquivo | Papel | O que mostra | Insight | Motivo da escolha |
|---|---|---|---|---|
| `01 - Distribuição por Renda` | Exploratória | Quantidade e percentual de pessoas em cada faixa de renda anual. | A base é desbalanceada, com 37.155 pessoas (76,1%) ate US$ 50 mil e 11.687 (23,9%) acima. Por isso, os demais gráficos comparam taxas e percentuais, e nao contagens. | Barras comparam duas categorias pelo comprimento, e o rotulo com numero e percentual evita depender do eixo. |
| `02 - Idade por Renda` | Exploratória | Distribuicao da idade dentro de cada faixa de renda, em percentual do proprio grupo. | Quem ganha acima de US$ 50 mil e mais velho (mediana de 43 anos, contra 34), mas as distribuicoes se sobrepoem bastante. | Histograma normalizado por grupo mostra forma e sobreposicao sem o efeito do desbalanceamento. |
| `03 - Escolaridade por Renda` | Exploratória | Composicao percentual das faixas de renda dentro de cada um dos 5 grupos de escolaridade (cada barra soma 100%). | A parcela com renda acima de US$ 50 mil vai de 5,5% ate a 8a serie a 48,1% em bacharelado ou mais, com o maior salto entre faculdade/associate (20,6%) e bacharelado. | Duas variáveis qualitativas: barras empilhadas em 100% mostram a composicao de cada grupo sem o efeito do desbalanceamento. |
| `04 - Renda por ocupação` | Exploratória | Taxa de renda acima de US$ 50 mil por ocupacao, para ocupacoes com pelo menos 100 pessoas. | A taxa vai de 1,2% no servico domestico a 47,8% em gerencia e direcao, entao a ocupacao tambem separa bem a renda. | Barras horizontais acomodam nomes longos e, ordenadas pela taxa, facilitam achar os extremos. |
| `05 - Pergunta por escolaridade` | Explanatória | Taxa de renda acima de US$ 50 mil em cada grupo de escolaridade, na ordem dos niveis de ensino. | A taxa fica perto de 6% ate a 12a serie, 15,9% no ensino medio completo, 20,6% em faculdade/associate e da um salto para 48,1% em bacharelado ou mais, contra 16,0% nos grupos abaixo. Responde diretamente à pergunta de pesquisa. | A ordem dos grupos mostra onde a taxa muda, a cor coral destaca so o bacharelado ou mais e o titulo diz a conclusao. |
| `06 - Escolaridade por Horas` | Explanatória | Taxa de renda acima de US$ 50 mil em cada faixa de horas semanais, com uma linha por grupo de escolaridade. Pontos com menos de 30 pessoas sao omitidos. | A taxa sobe com a jornada ate 41 a 50 horas e depois se estabiliza, mas a escolaridade pesa mais. Ensino medio completo com 51 horas ou mais (27,9%) fica abaixo de bacharelado ou mais com 40 horas (42,3%). | As faixas de horas sao ordenadas, entao linhas mostram a tendencia de cada grupo e a distancia entre eles, o que o mapa de calor anterior mostrava so pela intensidade da cor. |

As seis figuras são geradas pelo script `src/parte_especifica/visualizacoes.py` (com `pandas`, `matplotlib` e `seaborn`) e ficam em `out/parte_especifica/visualizacoes/`, em formato PNG, com os nomes da coluna Arquivo. A escolaridade aparece agrupada em 5 grupos (ate 8a serie; 9a a 12a sem diploma; ensino medio completo; faculdade sem diploma ou associate degree; bacharelado ou mais), mantendo a classificacao dos EUA. As mesmas seis visualizacoes aparecem no dashboard, cada uma com a sua nota analitica, e as notas completas estao no relatorio.
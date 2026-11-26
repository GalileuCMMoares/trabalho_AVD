"""Notas analiticas de cada visualizacao do dashboard (mesmo texto do relatorio).

Cada nota tem três partes: o que o grafico mostra, o insight e o motivo da escolha do grafico.
Os numeros se referem à base completa (48.842 pessoas), sem filtros.
"""

# [IA] Claude Code - notas analiticas exibidas no dashboard
# [IA] GitHub Copilot – revisão de pontuação do texto existente, sem gerar interpretações.

NOTAS = {
    "renda": (
        "Quantidade e percentual de pessoas em cada faixa de renda anual.",
        "A base é desbalanceada, com 37.155 pessoas (76,1%) ate US$ 50 mil e 11.687 (23,9%) acima. "
        "Por isso, os demais graficos comparam taxas e distribuicoes em percentual, e nao contagens absolutas.",
        "Barras comparam duas categorias pelo comprimento, e o rotulo com numero e percentual "
        "evita depender da leitura do eixo.",
    ),
    "idade": (
        "Distribuicao da idade dentro de cada faixa de renda, em percentual do proprio grupo.",
        "Quem ganha acima de US$ 50 mil e mais velho (mediana de 43 anos, contra 34). A taxa de renda alta "
        "e quase nula ate 25 anos (1,8%) e chega ao maximo entre 46 e 55 anos (39,2%). Mesmo assim, as duas "
        "distribuicoes se sobrepoem bastante, entao a idade sozinha nao separa as faixas.",
        "O histograma mostra forma e sobreposicao de uma variavel numerica, e a normalizacao dentro de cada "
        "grupo corrige o desbalanceamento da base.",
    ),
    "escolaridade": (
        "Composicao percentual das faixas de renda dentro de cada grupo de escolaridade (cada barra soma 100%).",
        "A parcela com renda acima de US$ 50 mil cresce a cada grupo: 5,5% ate a 8a serie, 5,8% da 9a a 12a "
        "serie sem diploma, 15,9% no ensino medio completo, 20,6% em faculdade sem diploma ou associate degree "
        "e 48,1% em bacharelado ou mais. O maior salto esta entre os dois ultimos grupos, e a escolaridade e a "
        "variavel que mais separa as faixas de renda.",
        "Escolaridade agrupada e faixa de renda sao duas variaveis qualitativas, entao barras empilhadas em 100% "
        "mostram a composicao de cada grupo sem o efeito do desbalanceamento da base.",
    ),
    "ocupacao": (
        "Taxa de renda acima de US$ 50 mil em cada ocupacao com pelo menos 100 pessoas no recorte.",
        "A taxa vai de 1,2% no servico domestico e 4,1% em outros servicos ate 45,1% em profissional "
        "especializado e 47,8% em gerencia e direcao. Pessoas sem ocupacao informada ficam em 9,4%. A "
        "ocupacao tambem separa bem a renda, entao parte da diferenca vista por escolaridade pode passar por ela.",
        "Barras horizontais acomodam nomes longos e, ordenadas pela taxa, facilitam achar os extremos.",
    ),
    "estado_civil": (
        "Taxa de renda acima de US$ 50 mil por estado civil, para grupos com pelo menos 100 pessoas.",
        "Casados no civil tem 44,6% de renda alta, contra 4,5% de quem nunca casou e 10,1% dos divorciados. "
        "Parte dessa diferenca vem da idade, ja que quem nunca casou e bem mais jovem (mediana de 25 anos, "
        "contra 42 dos casados no civil).",
        "Mesmo formato do grafico de ocupacao, para facilitar a comparacao entre os dois.",
    ),
    "jornada": (
        "Distribuicao das horas trabalhadas por semana em cada faixa de renda, em percentual do proprio grupo.",
        "As duas faixas tem mediana de 40 horas, mas 49,1% de quem ganha acima de US$ 50 mil trabalha mais "
        "de 40 horas, contra 23,2% de quem ganha ate esse valor. A diferenca esta na cauda de jornadas longas.",
        "Histogramas em paineis separados e com escala comum permitem comparar as distribuicoes sem sobreposicao; "
        "os percentuais sao calculados dentro de cada faixa de renda.",
    ),
    "pergunta": (
        "Taxa de renda acima de US$ 50 mil em cada grupo de escolaridade, na ordem dos niveis de ensino.",
        "Até a 12ª série sem diploma, a taxa fica perto de 6%. Ela sobe para 15,9% no ensino medio completo e "
        "20,6% em faculdade sem diploma ou associate degree, e da um salto para 48,1% em bacharelado ou mais, "
        "tres vezes a taxa do conjunto abaixo do bacharelado (16,0%). Este e o grafico que responde "
        "diretamente à pergunta de pesquisa.",
        "Com as barras na ordem dos niveis, a posicao mostra onde a taxa muda, e a cor destaca so o grupo de "
        "bacharelado ou mais, que concentra a diferenca. O titulo ja diz a conclusao.",
    ),
    "mapa": (
        "Taxa de renda acima de US$ 50 mil em cada faixa de horas semanais, com uma linha para cada grupo de "
        "escolaridade. Pontos com menos de 30 pessoas sao omitidos.",
        "Em todos os grupos, a taxa sobe com a jornada ate a faixa de 41 a 50 horas e depois quase nao muda "
        "(bacharelado ou mais vai de 60,6% para 62,4%). A escolaridade pesa mais que a jornada: quem tem "
        "ensino medio completo e trabalha 51 horas ou mais tem 27,9% de renda alta, menos do que quem tem "
        "bacharelado ou mais e trabalha 40 horas (42,3%). Ou seja, jornada longa nao compensa escolaridade baixa.",
        "As faixas de horas sao ordenadas, entao linhas mostram a tendencia de cada grupo ao longo da jornada e "
        "a distancia entre os grupos ao mesmo tempo. Com 5 grupos, a comparacao fica mais direta do que no mapa "
        "de calor usado antes, em que era preciso comparar intensidades de cor.",
    ),
}

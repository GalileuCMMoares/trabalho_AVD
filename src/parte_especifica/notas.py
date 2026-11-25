"""Notas analiticas de cada visualizacao do dashboard (mesmo texto do relatorio).

Cada nota tem tres partes, o que o grafico mostra, o insight e o motivo da escolha do grafico.
Os numeros se referem a base completa (48.842 pessoas), sem filtros.
"""

# [IA] Claude Code - notas analiticas exibidas no dashboard

NOTAS = {
    "renda": (
        "Quantidade e percentual de pessoas em cada faixa de renda anual.",
        "A base e desbalanceada, com 37.155 pessoas (76,1%) ate US$ 50 mil e 11.687 (23,9%) acima. "
        "Por isso os demais graficos comparam taxas e distribuicoes em percentual, e nao contagens absolutas.",
        "Barras comparam duas categorias pelo comprimento, e o rotulo com numero e percentual "
        "evita depender da leitura do eixo.",
    ),
    "idade": (
        "Distribuicao da idade dentro de cada faixa de renda, em percentual do proprio grupo.",
        "Quem ganha acima de US$ 50 mil e mais velho (mediana de 43 anos, contra 34). A taxa de renda alta "
        "e quase nula ate 25 anos (1,8%) e chega ao maximo entre 46 e 55 anos (39,2%). Mesmo assim as duas "
        "distribuicoes se sobrepoem bastante, entao a idade sozinha nao separa as faixas.",
        "O histograma mostra forma e sobreposicao de uma variavel numerica, e a normalizacao dentro de cada "
        "grupo corrige o desbalanceamento da base.",
    ),
    "escolaridade": (
        "Distribuicao percentual das faixas de renda dentro de cada nivel de escolaridade.",
        "Entre quem ganha ate US$ 50 mil, metade parou no ensino medio completo ou antes. Entre quem ganha "
        "acima, a mediana sobe para tecnologo academico e pelo menos um quarto tem graduacao ou mais. A "
        "escolaridade e a variavel que mais desloca a distribuicao entre as duas faixas.",
        "Barras empilhadas mostram a composicao percentual de duas variaveis categoricas em cada nivel.",
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
        "Taxa de renda acima de US$ 50 mil em cada grupo de escolaridade da base americana.",
        "A nota analítica deve ser revista pelo grupo com base nas taxas recalculadas para as categorias agrupadas.",
        "Barras ordenadas permitem comparar as taxas entre os mesmos grupos usados no grafico exploratorio.",
    ),
    "mapa": (
        "Taxa de renda acima de US$ 50 mil para cada combinacao de escolaridade e faixa de horas semanais. "
        "Celulas com menos de 30 pessoas ficam em branco.",
        "A interpretação deve ser revista pelo grupo para as novas categorias de escolaridade agrupadas.",
        "O mapa de calor cruza duas variaveis categorizadas e mostra a taxa pela intensidade da cor. Esconder "
        "as celulas pequenas evita que percentuais instaveis chamem atencao.",
    ),
}

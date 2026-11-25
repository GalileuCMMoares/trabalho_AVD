"""Rotulos em portugues para as categorias do Adult, usados no dashboard e nas figuras."""

import pandas as pd

# [IA] Claude Code - dicionarios de traducao das categorias do Adult e preparo das colunas traduzidas

RENDA = {"<=50K": "Ate US$ 50 mil", ">50K": "Acima de US$ 50 mil"}
ORDEM_RENDA = ["Ate US$ 50 mil", "Acima de US$ 50 mil"]
CORES_RENDA = {"Ate US$ 50 mil": "#77A7D1", "Acima de US$ 50 mil": "#E49B79"}
COR_DESTAQUE = "#E49B79"
COR_CONTEXTO = "#8DA5B8"

# education-num -> nome do nivel (traducao aproximada do sistema escolar dos EUA)
ESCOLARIDADE = {
    1: "Educacao infantil",
    2: "1a a 4a serie",
    3: "5a e 6a serie",
    4: "7a e 8a serie",
    5: "9a serie",
    6: "10a serie",
    7: "11a serie",
    8: "12a serie sem diploma",
    9: "Ensino medio completo",
    10: "Superior incompleto",
    11: "Tecnologo (profissional)",
    12: "Tecnologo (academico)",
    13: "Graduacao",
    14: "Mestrado",
    15: "Titulo profissional (Prof-school, EUA)",
    16: "Doutorado",
}
# Posicionamento de apresentacao; titulos profissionais e academicos nao
# formam necessariamente uma hierarquia linear de equivalencia.
ORDEM_CODIGOS_ESCOLARIDADE = list(range(1, 14)) + [15, 14, 16]
ORDEM_ESCOLARIDADE = [ESCOLARIDADE[n] for n in ORDEM_CODIGOS_ESCOLARIDADE]
ORDEM_ESCOLARIDADE_AGRUPADA = [
    "Até 8ª série (EUA)", "9ª a 12ª série, sem diploma (EUA)",
    "Ensino médio completo (EUA)", "Faculdade sem diploma ou associate degree (EUA)",
    "Bacharelado ou titulação superior (EUA)",
]
ESCOLARIDADE_AGRUPADA = {
    **{n: ORDEM_ESCOLARIDADE_AGRUPADA[0] for n in range(1, 5)},
    **{n: ORDEM_ESCOLARIDADE_AGRUPADA[1] for n in range(5, 9)},
    9: ORDEM_ESCOLARIDADE_AGRUPADA[2],
    **{n: ORDEM_ESCOLARIDADE_AGRUPADA[3] for n in range(10, 13)},
    **{n: ORDEM_ESCOLARIDADE_AGRUPADA[4] for n in range(13, 17)},
}
# Rotulos curtos e cores dos grupos (tons de cinza azulado e coral so no bacharelado ou mais)
ROTULOS_CURTOS_AGRUPADA = dict(zip(ORDEM_ESCOLARIDADE_AGRUPADA, [
    "Ate 8a serie", "9a a 12a sem diploma", "Ensino medio completo", "Faculdade / associate", "Bacharelado ou mais",
]))
CORES_ESCOLARIDADE_AGRUPADA = dict(zip(ORDEM_ESCOLARIDADE_AGRUPADA, [
    "#A9BCCB", "#89A2B6", "#6D88A0", "#56708A", COR_DESTAQUE,
]))
NIVEL_GRADUACAO = 13  # a partir deste education-num o nivel e graduacao ou mais

SEXO = {"Male": "Homem", "Female": "Mulher"}

OCUPACAO = {
    "Adm-clerical": "Administrativo",
    "Armed-Forces": "Forcas Armadas",
    "Craft-repair": "Oficios e reparos",
    "Exec-managerial": "Gerencia e direcao",
    "Farming-fishing": "Agricultura e pesca",
    "Handlers-cleaners": "Carga e limpeza",
    "Machine-op-inspct": "Operacao de maquinas",
    "Other-service": "Outros servicos",
    "Priv-house-serv": "Servico domestico",
    "Prof-specialty": "Profissional especializado",
    "Protective-serv": "Seguranca",
    "Sales": "Vendas",
    "Tech-support": "Suporte tecnico",
    "Transport-moving": "Transporte",
}

ESTADO_CIVIL = {
    "Married-civ-spouse": "Casado no civil",
    "Never-married": "Nunca casou",
    "Divorced": "Divorciado",
    "Separated": "Separado",
    "Widowed": "Viuvo",
    "Married-spouse-absent": "Casado com conjuge ausente",
    "Married-AF-spouse": "Casado com conjuge militar",
}

TIPO_TRABALHO = {
    "Private": "Setor privado",
    "Self-emp-not-inc": "Autonomo",
    "Self-emp-inc": "Empresario",
    "Federal-gov": "Governo federal",
    "State-gov": "Governo estadual",
    "Local-gov": "Governo local",
    "Without-pay": "Sem remuneracao",
    "Never-worked": "Nunca trabalhou",
}

RACA = {
    "White": "Branca",
    "Black": "Negra",
    "Asian-Pac-Islander": "Asiatica ou ilhas do Pacifico",
    "Amer-Indian-Eskimo": "Indigena",
    "Other": "Outra",
}

RELACAO = {
    "Husband": "Marido",
    "Wife": "Esposa",
    "Own-child": "Filho ou filha",
    "Not-in-family": "Fora da familia",
    "Other-relative": "Outro parente",
    "Unmarried": "Nao casado",
}

FAIXAS_HORAS = ["ate 20", "21 a 39", "40", "41 a 50", "51 ou mais"]
LIMITES_HORAS = [0, 20, 39, 40, 50, float("inf")]


def traduzir(serie: pd.Series, mapa: dict) -> pd.Series:
    """Traduz os valores conhecidos e marca ausentes como Desconhecido."""
    return serie.map(mapa).fillna(serie).fillna("Desconhecido")


def preparar_adult(df: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta ao Adult as colunas usadas nos graficos, sem alterar as originais."""
    df = df.copy()
    df["income"] = df["income"].astype(str).str.strip().str.rstrip(".")
    df["alta_renda"] = df["income"].eq(">50K")
    df["renda"] = pd.Categorical(df["income"].map(RENDA), categories=ORDEM_RENDA, ordered=True)
    df["escolaridade"] = pd.Categorical(
        df["education-num"].map(ESCOLARIDADE), categories=ORDEM_ESCOLARIDADE, ordered=True
    )
    df["escolaridade_agrupada"] = pd.Categorical(
        df["education-num"].map(ESCOLARIDADE_AGRUPADA),
        categories=ORDEM_ESCOLARIDADE_AGRUPADA, ordered=True,
    )
    df["graduacao_ou_mais"] = df["education-num"] >= NIVEL_GRADUACAO
    df["sexo"] = traduzir(df["sex"], SEXO)
    df["ocupacao"] = traduzir(df["occupation"], OCUPACAO)
    df["estado_civil"] = traduzir(df["marital-status"], ESTADO_CIVIL)
    df["tipo_trabalho"] = traduzir(df["workclass"], TIPO_TRABALHO)
    df["raca"] = traduzir(df["race"], RACA)
    df["relacao_familiar"] = traduzir(df["relationship"], RELACAO)
    df["faixa_horas"] = pd.cut(
        df["hours-per-week"], bins=LIMITES_HORAS, labels=FAIXAS_HORAS, include_lowest=True
    )
    return df


def pct(valor: float, casas: int = 1) -> str:
    """Formata proporcao como percentual no padrao brasileiro (23,9%)."""
    return f"{valor * 100:.{casas}f}%".replace(".", ",")


def inteiro(valor: int) -> str:
    """Formata inteiro com ponto de milhar (37.155)."""
    return f"{int(valor):,}".replace(",", ".")

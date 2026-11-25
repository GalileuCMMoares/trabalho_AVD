"""Dashboard interativo do projeto de AVD.

Pagina principal com a Parte Especifica (dataset Adult) e pagina extra com a Parte Comum (dataset Obesity).
Execucao, streamlit run src/parte_especifica/dashboard.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from notas import NOTAS
from traducoes import (
    COR_CONTEXTO,
    COR_DESTAQUE,
    CORES_ESCOLARIDADE_AGRUPADA,
    CORES_RENDA,
    ESCOLARIDADE,
    FAIXAS_HORAS,
    ORDEM_ESCOLARIDADE,
    ORDEM_ESCOLARIDADE_AGRUPADA,
    ORDEM_CODIGOS_ESCOLARIDADE,
    ORDEM_RENDA,
    inteiro,
    pct,
    preparar_adult,
)

# [IA] Codex - apoio tecnico com Streamlit, pandas e Plotly para estruturar o dashboard e seus filtros
# [IA] Claude Code - rotulos em portugues, notas analiticas, graficos normalizados por grupo, mapa de calor
# com mascara de celulas pequenas, explorador de duas variaveis e pagina da Parte Comum com K-Means
ROOT = Path(__file__).resolve().parents[2]
ADULT_PATH = ROOT / "data" / "parte_especifica" / "adult.csv"
OBESITY_PATH = ROOT / "data" / "parte_comum" / "ObesityDataSet_raw_and_data_sinthetic.csv"
MINIMO_GRUPO = 100
MINIMO_CELULA = 30
COLUNAS_ORIGINAIS = [
    "age", "workclass", "fnlwgt", "education", "education-num", "marital-status", "occupation",
    "relationship", "race", "sex", "capital-gain", "capital-loss", "hours-per-week", "native-country", "income",
]
CLASSES_OBESITY = [
    "Insufficient_Weight", "Normal_Weight", "Overweight_Level_I", "Overweight_Level_II",
    "Obesity_Type_I", "Obesity_Type_II", "Obesity_Type_III",
]
# Nomes em portugues e cores na ordem do IMC (azul = abaixo do peso, vermelho = obesidade III), iguais aos da EDA
NOMES_CLASSES = {
    "Insufficient_Weight": "Abaixo do peso", "Normal_Weight": "Peso normal",
    "Overweight_Level_I": "Sobrepeso I", "Overweight_Level_II": "Sobrepeso II",
    "Obesity_Type_I": "Obesidade I", "Obesity_Type_II": "Obesidade II", "Obesity_Type_III": "Obesidade III",
}
ORDEM_NOMES_CLASSES = [NOMES_CLASSES[c] for c in CLASSES_OBESITY]
CORES_CLASSES = px.colors.sample_colorscale("RdYlBu_r", [i / 6 for i in range(7)])
K_LIVRE, K_FIXO = 4, 7
ROTULOS_ESCOLARIDADE_CURTOS = [
    "Até 8ª série", "9ª–12ª sem diploma", "Ensino médio completo",
    "Faculdade / associate", "Bacharelado ou mais",
]
MACRO_CLASSES = {
    "Insufficient_Weight": "Abaixo do Peso", "Normal_Weight": "Normal",
    "Overweight_Level_I": "Sobrepeso", "Overweight_Level_II": "Sobrepeso",
    "Obesity_Type_I": "Obesidade", "Obesity_Type_II": "Obesidade", "Obesity_Type_III": "Obesidade",
}
ORDEM_MACRO = ["Abaixo do Peso", "Normal", "Sobrepeso", "Obesidade"]

st.set_page_config(page_title="Projeto AVD", page_icon="📊", layout="wide", initial_sidebar_state="expanded")


# ---------------------------------------------------------------- utilidades

def mostrar(fig: go.Figure) -> None:
    """Exibe o grafico com numeros no padrao brasileiro (virgula decimal e ponto de milhar)."""
    fig.update_layout(separators=",.", margin=dict(l=10, r=30, t=80, b=10))
    st.plotly_chart(fig, width="stretch")


def nota(chave: str) -> None:
    o_que, insight, porque = NOTAS[chave]
    with st.expander("Nota analitica (valores da base completa)"):
        st.markdown(f"**O que mostra.** {o_que}\n\n**Insight.** {insight}\n\n**Por que este grafico.** {porque}")


def taxa_por(df: pd.DataFrame, coluna: str, minimo: int = 0) -> pd.DataFrame:
    tabela = df.groupby(coluna, observed=True)["alta_renda"].agg(taxa="mean", pessoas="size").reset_index()
    tabela = tabela[tabela["pessoas"] >= minimo].copy()
    tabela["percentual"] = tabela["taxa"] * 100
    return tabela


# ---------------------------------------------------------------- Parte Especifica (Adult)

@st.cache_data
def carregar_adult(caminho: str) -> pd.DataFrame:
    return preparar_adult(pd.read_csv(caminho))


def grafico_taxa_por_categoria(df: pd.DataFrame, coluna: str, rotulo: str, titulo: str) -> None:
    tabela = taxa_por(df, coluna, MINIMO_GRUPO).sort_values("taxa")
    if tabela.empty:
        st.info(f"Nenhum grupo de {rotulo.lower()} tem pelo menos {MINIMO_GRUPO} pessoas no recorte atual.")
        return
    fig = px.bar(
        tabela,
        x="percentual",
        y=coluna,
        orientation="h",
        hover_data={"pessoas": ":,", "percentual": ":.1f"},
        labels={"percentual": "% com renda acima de US$ 50 mil", coluna: rotulo, "pessoas": "Pessoas"},
        title=titulo,
        color_discrete_sequence=[CORES_RENDA["Ate US$ 50 mil"]],
    )
    fig.update_traces(texttemplate="%{x:.1f}%", textposition="outside", cliponaxis=False)
    fig.update_layout(showlegend=False, xaxis_range=[0, max(60, tabela["percentual"].max() * 1.15)])
    mostrar(fig)
    st.caption(f"Apenas grupos com pelo menos {MINIMO_GRUPO} pessoas no recorte.")


def histograma_por_renda(df: pd.DataFrame, coluna: str, rotulo: str, titulo: str, nbins: int) -> None:
    fig = px.histogram(
        df,
        x=coluna,
        color="renda",
        facet_row="renda",
        histnorm="percent",
        nbins=nbins,
        color_discrete_map=CORES_RENDA,
        category_orders={"renda": ORDEM_RENDA},
        labels={coluna: rotulo, "renda": "Faixa de renda"},
        title=titulo,
    )
    fig.for_each_annotation(lambda anotacao: anotacao.update(text=anotacao.text.split("=")[-1], textangle=0))
    fig.update_yaxes(matches="y", title_text="% da faixa de renda")
    fig.update_layout(showlegend=False, height=650)
    mostrar(fig)
    st.caption("Cada painel mostra a distribuição percentual dentro de uma faixa de renda; os eixos usam a mesma escala.")


def grafico_jornada_por_renda(df: pd.DataFrame) -> None:
    """Compara distribuicoes em paineis separados, com escala comum."""
    fig = px.histogram(
        df, x="hours-per-week", color="renda", facet_col="renda",
        histnorm="percent", nbins=40, color_discrete_map=CORES_RENDA,
        category_orders={"renda": ORDEM_RENDA},
        labels={"hours-per-week": "Horas trabalhadas por semana", "renda": "Faixa de renda"},
        title="Distribuição da jornada semanal por faixa de renda",
    )
    fig.for_each_annotation(lambda anotacao: anotacao.update(text=anotacao.text.split("=")[-1]))
    fig.update_yaxes(matches="y", title_text="% dentro da faixa de renda")
    fig.update_layout(showlegend=False)
    mostrar(fig)
    st.caption("Cada painel mostra percentuais calculados dentro da respectiva faixa de renda, usando a mesma escala vertical.")


def grafico_distribuicao_renda(df: pd.DataFrame) -> None:
    contagem = (
        df["renda"].value_counts().reindex(ORDEM_RENDA, fill_value=0).rename_axis("renda").reset_index(name="pessoas")
    )
    contagem["percentual"] = contagem["pessoas"] / contagem["pessoas"].sum() * 100
    fig = px.bar(
        contagem,
        x="renda",
        y="pessoas",
        color="renda",
        color_discrete_map=CORES_RENDA,
        custom_data=["percentual"],
        labels={"renda": "Faixa de renda anual", "pessoas": "Numero de pessoas"},
        title="Distribuicao da faixa de renda",
    )
    fig.update_traces(texttemplate="%{y:,.0f}<br>(%{customdata[0]:.1f}%)", textposition="outside", cliponaxis=False)
    fig.update_layout(showlegend=False, yaxis_range=[0, contagem["pessoas"].max() * 1.2])
    mostrar(fig)


def grafico_escolaridade_box(df: pd.DataFrame) -> None:
    tabela = df.groupby(["escolaridade_agrupada", "renda"], observed=True).size().reset_index(name="pessoas")
    tabela["percentual"] = tabela["pessoas"] / tabela.groupby("escolaridade_agrupada", observed=True)["pessoas"].transform("sum") * 100
    fig = px.bar(
        tabela,
        x="percentual",
        y="escolaridade_agrupada",
        color="renda",
        orientation="h",
        color_discrete_map=CORES_RENDA,
        category_orders={"renda": ORDEM_RENDA, "escolaridade_agrupada": ORDEM_ESCOLARIDADE_AGRUPADA},
        hover_data={"pessoas": True, "percentual": ":.1f"},
        labels={"renda": "Faixa de renda anual", "escolaridade_agrupada": "Escolaridade agrupada", "percentual": "% de pessoas no nivel", "pessoas": "Pessoas"},
        title="Faixa de renda em cada nivel de escolaridade",
    )
    fig.update_layout(barmode="stack", height=650, xaxis_range=[0, 100])
    fig.update_yaxes(categoryorder="array", categoryarray=ORDEM_ESCOLARIDADE_AGRUPADA,
                     tickmode="array", tickvals=ORDEM_ESCOLARIDADE_AGRUPADA,
                     ticktext=ROTULOS_ESCOLARIDADE_CURTOS)
    mostrar(fig)
    st.caption("Cada barra representa 100% das pessoas naquele nivel de escolaridade no recorte selecionado.")
    st.caption("Categorias agrupadas a partir da classificação dos EUA, sem equivalência formal com o sistema brasileiro. 'Faculdade sem diploma ou associate degree' reúne Some-college, Assoc-voc e Assoc-acdm.")


def grafico_pergunta(df: pd.DataFrame) -> None:
    tabela = taxa_por(df, "escolaridade_agrupada")
    tabela["grupo"] = np.where(tabela["escolaridade_agrupada"] == ORDEM_ESCOLARIDADE_AGRUPADA[-1], "Bacharelado ou mais", "Abaixo do bacharelado")
    sup = df.loc[df["graduacao_ou_mais"], "alta_renda"]
    inf = df.loc[~df["graduacao_ou_mais"], "alta_renda"]
    if len(sup) and len(inf):
        titulo = (f"Com bacharelado ou mais, {pct(sup.mean())} tem renda acima de US$ 50 mil<br>"
                  f"contra {pct(inf.mean())} nos grupos abaixo do bacharelado")
    else:
        titulo = "Taxa de renda acima de US$ 50 mil por escolaridade"
    fig = px.bar(
        tabela,
        x="percentual",
        y="escolaridade_agrupada",
        orientation="h",
        color="grupo",
        color_discrete_map={"Bacharelado ou mais": COR_DESTAQUE, "Abaixo do bacharelado": COR_CONTEXTO},
        category_orders={"escolaridade_agrupada": ORDEM_ESCOLARIDADE_AGRUPADA, "grupo": ["Bacharelado ou mais", "Abaixo do bacharelado"]},
        hover_data={"pessoas": ":,", "grupo": False},
        labels={"percentual": "% com renda acima de US$ 50 mil", "escolaridade_agrupada": "Escolaridade agrupada (EUA)", "pessoas": "Pessoas"},
        title=titulo,
    )
    fig.update_traces(texttemplate="%{x:.0f}%", textposition="outside", cliponaxis=False)
    fig.update_layout(height=580, legend_title_text="", xaxis_showgrid=False, xaxis_range=[0, 100])
    fig.update_yaxes(categoryorder="array", categoryarray=ORDEM_ESCOLARIDADE_AGRUPADA,
                     tickmode="array", tickvals=ORDEM_ESCOLARIDADE_AGRUPADA,
                     ticktext=ROTULOS_ESCOLARIDADE_CURTOS)
    mostrar(fig)
    st.caption("Categorias da base americana agrupadas sem equivalência formal com o sistema brasileiro.")


def grafico_mapa_calor(df: pd.DataFrame) -> None:
    """Taxa de renda alta por faixa de horas, uma linha por grupo de escolaridade."""
    # [IA] Claude Code - troca do mapa de calor por linhas, pedida no feedback da professora
    faixa = df["faixa_horas"].astype(str)
    taxa = pd.crosstab(df["escolaridade_agrupada"], faixa, values=df["alta_renda"], aggfunc="mean").reindex(
        index=ORDEM_ESCOLARIDADE_AGRUPADA, columns=FAIXAS_HORAS)
    contagem = pd.crosstab(df["escolaridade_agrupada"], faixa).reindex(index=taxa.index, columns=FAIXAS_HORAS).fillna(0)
    z = (taxa * 100).where(contagem >= MINIMO_CELULA)
    fig = go.Figure()
    for grupo, curto in zip(ORDEM_ESCOLARIDADE_AGRUPADA, ROTULOS_ESCOLARIDADE_CURTOS):
        forte = grupo == ORDEM_ESCOLARIDADE_AGRUPADA[-1]
        fig.add_trace(go.Scatter(
            x=FAIXAS_HORAS, y=z.loc[grupo].to_numpy(), name=curto, mode="lines+markers",
            line=dict(color=CORES_ESCOLARIDADE_AGRUPADA[grupo], width=4 if forte else 2.5),
            customdata=contagem.loc[grupo].to_numpy().astype(int),
            hovertemplate=f"{curto}<br>Jornada %{{x}} horas<br>%{{y:.1f}}% com renda acima de US$ 50 mil"
                          "<br>%{customdata} pessoas<extra></extra>",
        ))
    fig.update_layout(
        title="Jornada longa nao compensa escolaridade baixa",
        xaxis_title="Horas trabalhadas por semana",
        yaxis_title="% com renda acima de US$ 50 mil",
        yaxis_range=[0, 80],
        legend_title_text="Escolaridade",
        legend_traceorder="reversed",
        height=560,
    )
    mostrar(fig)
    st.caption(f"Pontos com menos de {MINIMO_CELULA} pessoas no recorte sao omitidos para evitar percentuais instaveis.")


VARIAVEIS = {
    "Idade": ("age", "num"),
    "Horas por semana": ("hours-per-week", "num"),
    "Nivel de escolaridade (1 a 16)": ("education-num", "num"),
    "Ganho de capital": ("capital-gain", "num"),
    "Perda de capital": ("capital-loss", "num"),
    "Escolaridade": ("escolaridade", "cat"),
    "Faixa de renda": ("renda", "cat"),
    "Faixa de horas": ("faixa_horas", "cat"),
    "Sexo": ("sexo", "cat"),
    "Estado civil": ("estado_civil", "cat"),
    "Ocupacao": ("ocupacao", "cat"),
    "Tipo de trabalho": ("tipo_trabalho", "cat"),
    "Raca": ("raca", "cat"),
    "Relacao familiar": ("relacao_familiar", "cat"),
}
ORDENS_FIXAS = {"escolaridade": ORDEM_ESCOLARIDADE, "renda": ORDEM_RENDA, "faixa_horas": FAIXAS_HORAS}


def ordem_categorias(df: pd.DataFrame, coluna: str) -> list:
    if coluna in ORDENS_FIXAS:
        presentes = set(df[coluna].astype(str))
        return [c for c in ORDENS_FIXAS[coluna] if c in presentes]
    return df[coluna].astype(str).value_counts().index.tolist()


def categorias_explorador(df: pd.DataFrame, coluna: str) -> tuple[pd.Series, list[str]]:
    """Prepara categorias ordenadas para os graficos de composicao."""
    if coluna == "age":
        limites, nomes = [16, 25, 35, 45, 55, 65, float("inf")], ["17–25", "26–35", "36–45", "46–55", "56–65", "66 ou mais"]
    elif coluna == "hours-per-week":
        return df["faixa_horas"].astype("string").fillna("Desconhecido"), FAIXAS_HORAS
    elif coluna == "education-num" or coluna == "escolaridade":
        return df["escolaridade_agrupada"].astype("string").fillna("Desconhecido"), ORDEM_ESCOLARIDADE_AGRUPADA
    elif coluna in ("capital-gain", "capital-loss"):
        limites, nomes = [-float("inf"), 0, 5000, 10000, float("inf")], ["Sem valor", "1–5.000", "5.001–10.000", "Acima de 10.000"]
    else:
        valores = df[coluna].astype("string").fillna("Desconhecido")
        ordem = ordem_categorias(df, coluna)
        if "Desconhecido" in valores.values and "Desconhecido" not in ordem:
            ordem.append("Desconhecido")
        return valores, ordem
    valores = pd.cut(df[coluna], bins=limites, labels=nomes, include_lowest=True)
    return valores.astype("string").fillna("Desconhecido"), nomes


def explorador(df: pd.DataFrame) -> None:
    st.subheader("Explorar a relação entre duas variáveis")
    st.caption("Todos os cruzamentos usam barras empilhadas. Variáveis numéricas são apresentadas em faixas fixas.")
    nomes = list(VARIAVEIS)
    esquerda, direita, extra = st.columns((1, 1, 1))
    nome_a = esquerda.selectbox("Primeira variável", nomes, index=nomes.index("Escolaridade"))
    nome_b = direita.selectbox("Segunda variável", nomes, index=nomes.index("Horas por semana"))
    separar = extra.checkbox("Separar por faixa de renda", value=False)
    if nome_a == nome_b:
        st.info("Escolha duas variáveis diferentes.")
        return

    col_a, _ = VARIAVEIS[nome_a]
    col_b, _ = VARIAVEIS[nome_b]
    if separar and "renda" in (col_a, col_b):
        st.caption("A separação adicional por renda não se aplica quando a renda já é uma das variáveis.")
        separar = False

    valores_a, ordem_a = categorias_explorador(df, col_a)
    valores_b, ordem_b = categorias_explorador(df, col_b)
    dados = pd.DataFrame({"primeira": valores_a, "segunda": valores_b, "renda": df["renda"].astype("string")}, index=df.index)
    grupos_renda = [r for r in ORDEM_RENDA if (dados["renda"] == r).any()] if separar else [None]
    for renda in grupos_renda:
        recorte = dados.loc[dados["renda"] == renda] if renda else dados
        tabela = recorte.groupby(["primeira", "segunda"], observed=True, dropna=False).size().reset_index(name="pessoas")
        tabela["percentual"] = tabela["pessoas"] / tabela.groupby("primeira")["pessoas"].transform("sum") * 100
        titulo = f"{nome_b} por {nome_a}" + (f" — {renda}" if renda else "")
        fig = px.bar(
            tabela, x="percentual", y="primeira", color="segunda", orientation="h",
            category_orders={"primeira": ordem_a, "segunda": ordem_b},
            color_discrete_map=CORES_RENDA if col_b == "renda" else None,
            labels={"percentual": "% dentro do grupo", "primeira": nome_a, "segunda": nome_b, "pessoas": "Pessoas"},
            hover_data={"pessoas": True, "percentual": ":.1f"}, title=titulo,
        )
        fig.update_layout(barmode="stack", height=max(400, 38 * len(ordem_a) + 170), xaxis_range=[0, 100])
        fig.update_yaxes(categoryorder="array", categoryarray=list(reversed(ordem_a)))
        mostrar(fig)

    st.caption("Cada barra soma 100% dentro da primeira variável" + (" e da faixa de renda indicada." if separar else ".") +
               " Passe o mouse sobre os segmentos para ver o percentual e o número de pessoas.")
    st.caption("Idade: 17–25, 26–35, 36–45, 46–55, 56–65 e 66+ anos. Jornada: até 20, 21–39, 40, 41–50 e 51+ horas. Capital: zero, 1–5.000, 5.001–10.000 e acima de 10.000. Escolaridade: cinco grupos da classificação dos EUA, sem equivalência formal com o Brasil.")


def pagina_especifica() -> None:
    if not ADULT_PATH.exists():
        st.error("Dataset nao encontrado em data/parte_especifica/adult.csv.")
        st.code("python src/parte_especifica/download_data.py", language="bash")
        st.stop()

    df = carregar_adult(str(ADULT_PATH))

    st.title("📊 Adult Income Explorer")
    st.write("Exploracao interativa da base Adult, com perfis sociodemograficos, trabalho, escolaridade e faixa de renda anual.")
    st.info("Leitura descritiva. Os graficos mostram associacoes presentes na amostra e nao demonstram relacoes de causa e efeito.", icon="ℹ️")

    with st.sidebar:
        st.header("Filtros")
        opcoes_sexo = sorted(df["sexo"].unique())
        sexo = st.multiselect("Sexo", opcoes_sexo, default=opcoes_sexo)
        opcoes_trabalho = sorted(df["tipo_trabalho"].unique())
        tipos = st.multiselect("Tipo de trabalho", opcoes_trabalho, default=opcoes_trabalho)
        faixa_idade = st.slider("Faixa de idade", 17, 90, (17, 90))
        faixa_horas = st.slider("Horas trabalhadas por semana", 1, 99, (1, 99))
        st.divider()
        st.caption("Os filtros atualizam todos os indicadores e graficos desta pagina.")

    filtrado = df.loc[
        df["sexo"].isin(sexo)
        & df["tipo_trabalho"].isin(tipos)
        & df["age"].between(*faixa_idade)
        & df["hours-per-week"].between(*faixa_horas)
    ]
    if filtrado.empty:
        st.warning("Nenhum registro atende aos filtros atuais. Ajuste os filtros na barra lateral.")
        st.stop()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pessoas selecionadas", inteiro(len(filtrado)), border=True)
    col2.metric("Renda acima de US$ 50 mil", pct(filtrado["alta_renda"].mean()), border=True)
    col3.metric("Idade mediana", f"{filtrado['age'].median():.0f} anos", border=True)
    col4.metric("Jornada mediana", f"{filtrado['hours-per-week'].median():.0f} h por semana", border=True)

    aba_visao, aba_exploracao, aba_pergunta, aba_explorar, aba_dados = st.tabs(
        ["Visao geral", "Exploracao", "Pergunta de pesquisa", "Explorar duas variaveis", "Dados"]
    )

    with aba_visao:
        st.subheader("Panorama da amostra filtrada")
        st.caption("A distribuicao da renda orienta a leitura dos demais graficos.")
        esquerda, direita = st.columns((1, 1.25))
        with esquerda:
            grafico_distribuicao_renda(filtrado)
            nota("renda")
        with direita:
            histograma_por_renda(filtrado, "age", "Idade (anos)", "Distribuicao de idade por faixa de renda", 30)
            nota("idade")

    with aba_exploracao:
        st.subheader("Exploracao dos perfis")
        st.caption("Use os filtros para investigar grupos e comparar padroes da amostra.")
        esquerda, direita = st.columns(2)
        with esquerda:
            grafico_escolaridade_box(filtrado)
            nota("escolaridade")
        with direita:
            grafico_taxa_por_categoria(filtrado, "ocupacao", "Ocupacao", "Taxa de renda acima de US$ 50 mil por ocupacao")
            nota("ocupacao")
        esquerda, direita = st.columns(2)
        with esquerda:
            grafico_taxa_por_categoria(filtrado, "estado_civil", "Estado civil", "Taxa de renda acima de US$ 50 mil por estado civil")
            nota("estado_civil")
        with direita:
            grafico_jornada_por_renda(filtrado)
            nota("jornada")

    with aba_pergunta:
        st.subheader("Pergunta de pesquisa")
        st.caption(
            "Como a escolaridade se associa a proporcao de pessoas com renda anual acima de US$ 50 mil, "
            "e como as horas trabalhadas ajudam a contextualizar essa associacao? A resposta se limita aos registros filtrados."
        )
        with st.expander("Entenda os grupos de escolaridade"):
            for curto, completo in zip(ROTULOS_ESCOLARIDADE_CURTOS, ORDEM_ESCOLARIDADE_AGRUPADA):
                st.markdown(f"**{curto}:** {completo}")
            st.caption("Classificação dos EUA, agrupada para visualização, sem equivalência formal com o sistema brasileiro.")
        grafico_pergunta(filtrado)
        nota("pergunta")
        grafico_mapa_calor(filtrado)
        nota("mapa")
        st.warning(
            "Nao interprete diferencas como causalidade. Idade, ocupacao, estado civil e outras variaveis "
            "tambem podem estar associadas ao mesmo tempo a escolaridade, a jornada e a renda.",
            icon="⚠️",
        )

    with aba_explorar:
        explorador(filtrado)

    with aba_dados:
        st.subheader("Dados e transparencia")
        st.write("Pre visualizacao da base original apos a aplicacao dos filtros.")
        st.dataframe(filtrado[COLUNAS_ORIGINAIS], width="stretch", height=380)
        st.download_button(
            "Baixar recorte filtrado em CSV",
            data=filtrado[COLUNAS_ORIGINAIS].to_csv(index=False).encode("utf-8"),
            file_name="adult_filtrado.csv",
            mime="text/csv",
        )
        st.caption("Fonte, UCI Machine Learning Repository, Adult (Becker e Kohavi, 1996).")


# ---------------------------------------------------------------- Parte Comum (Obesity)

def transformar_obesity(df: pd.DataFrame) -> pd.DataFrame:
    """Mesma feature transformation do notebook kmeans_metricas.ipynb (20 variaveis antes do StandardScaler)."""
    X = df.drop(columns=["NObeyesdad"]).copy()
    for col in ["family_history_with_overweight", "FAVC", "SMOKE", "SCC"]:
        X[col] = X[col].map({"no": 0, "yes": 1})
    X["Gender"] = X["Gender"].map({"Female": 0, "Male": 1})
    for col in ["CAEC", "CALC"]:
        X[col] = X[col].map({"no": 0, "Sometimes": 1, "Frequently": 2, "Always": 3})
    return pd.get_dummies(X, columns=["MTRANS"], prefix="MTRANS", dtype=int)


@st.cache_data
def preparar_comum(caminho: str):
    """Reproduz o notebook kmeans_metricas.ipynb (transformacao, padronizacao, PCA e K-Means de k = 2 a 10)."""
    df = pd.read_csv(caminho).drop_duplicates().reset_index(drop=True)
    X = StandardScaler().fit_transform(transformar_obesity(df))
    pca = PCA(n_components=2, random_state=42).fit(X)
    rotulos, inercias = {}, {}
    for k in range(2, 11):
        modelo = KMeans(n_clusters=k, random_state=42, n_init=10).fit(X)
        rotulos[k], inercias[k] = modelo.labels_, modelo.inertia_
    return df, pca.transform(X), pca.explained_variance_ratio_ * 100, rotulos, inercias


def avaliar_passada(rotulos: np.ndarray, y: pd.Series):
    """Mapeia cada cluster para a classe majoritaria e calcula matriz de confusao e metricas."""
    composicao = pd.crosstab(pd.Series(rotulos, name="cluster"), y.rename("classe"))
    mapa = composicao.idxmax(axis=1)
    y_mapeado = pd.Series(rotulos).map(mapa)
    previstas = [c for c in CLASSES_OBESITY if c in set(mapa)]
    matriz = pd.crosstab(y.rename("Classe real"), y_mapeado.rename("Rotulo mapeado")).reindex(
        index=CLASSES_OBESITY, columns=previstas, fill_value=0
    )
    acertos = pd.Series({c: matriz.loc[c, c] if c in previstas else 0 for c in CLASSES_OBESITY})
    total_previsto = matriz.sum(axis=0).reindex(CLASSES_OBESITY, fill_value=0)
    metricas = pd.DataFrame({
        "precisao": (acertos / total_previsto.replace(0, np.nan)).fillna(0),
        "recall": acertos / matriz.sum(axis=1),
    })
    acuracia = float((y_mapeado.to_numpy() == y.to_numpy()).mean())
    return matriz, metricas, acuracia, len(previstas)


def pagina_comum() -> None:
    st.title("🧩 Parte Comum, K-Means no dataset Obesity")
    st.write(
        "Resultados do notebook kmeans_metricas.ipynb (20 variaveis padronizadas, sendo as 8 numericas e as categoricas "
        "transformadas em binarias, ordinais e One-Hot, com random_state 42 e n_init 10). "
        f"A Passada 1 usa k = {K_LIVRE}, escolhido pelo Metodo do Cotovelo, e a Passada 2 usa k = {K_FIXO}, o numero real de classes."
    )
    if not OBESITY_PATH.exists():
        st.error("Dataset nao encontrado em data/parte_comum/.")
        st.stop()
    df, coords, var_exp, rotulos, inercias = preparar_comum(str(OBESITY_PATH))
    y = df["NObeyesdad"]
    eixo_x = f"Componente principal 1 ({var_exp[0]:.1f}% da variancia)".replace(".", ",")
    eixo_y = f"Componente principal 2 ({var_exp[1]:.1f}% da variancia)".replace(".", ",")
    pontos = pd.DataFrame({"pc1": coords[:, 0], "pc2": coords[:, 1], "classe": y.map(NOMES_CLASSES)})

    aba_cotovelo, aba_lado, aba_animacao, aba_macro = st.tabs(
        ["Metodo do Cotovelo", "Clusters e classes lado a lado", "Transicao entre as passadas",
         "4 macro-classes e verificacao"]
    )

    with aba_cotovelo:
        tabela = pd.DataFrame({"k": list(inercias), "inercia": list(inercias.values())})
        tabela["queda em relacao ao k anterior"] = -tabela["inercia"].diff()
        fig = px.line(tabela, x="k", y="inercia", markers=True,
                      labels={"k": "Numero de clusters (k)", "inercia": "Inercia (WCSS)"},
                      title="Metodo do Cotovelo, inercia para k de 2 a 10")
        fig.add_vline(x=K_LIVRE, line_dash="dash", line_color=COR_DESTAQUE,
                      annotation_text=f"Passada 1 (k = {K_LIVRE})", annotation_position="top right")
        fig.add_vline(x=K_FIXO, line_dash="dot", line_color="#555555",
                      annotation_text=f"Passada 2 (k = {K_FIXO})", annotation_position="top right")
        fig.update_xaxes(dtick=1)
        mostrar(fig)
        st.dataframe(tabela.round(1), width="stretch", hide_index=True)

    with aba_lado:
        k = st.slider("Numero de clusters (k)", 2, 10, K_LIVRE)
        matriz, metricas, acuracia, representadas = avaliar_passada(rotulos[k], y)
        m1, m2, m3 = st.columns(3)
        m1.metric("Acuracia (cluster mapeado para a classe majoritaria)", pct(acuracia))
        m2.metric("Classes representadas", f"{representadas} de {len(CLASSES_OBESITY)}")
        m3.metric("Baseline (sempre a classe mais frequente)", pct(y.value_counts(normalize=True).max()))
        # [IA] Claude Code - opcao de um painel por cluster para evitar a sobreposicao de cores
        paineis = st.toggle("Mostrar um painel por cluster (sem sobreposicao)", value=False)
        if paineis:
            quadros = []
            for c in range(k):
                dentro = rotulos[k] == c
                quadros.append(pontos.assign(
                    painel=f"Cluster {c} · n = {dentro.sum()}",
                    grupo=np.where(dentro, "Neste cluster", "Demais pontos"),
                ))
            quadros = pd.concat(quadros).sort_values("grupo")
            fig = px.scatter(quadros, x="pc1", y="pc2", color="grupo", facet_col="painel", facet_col_wrap=3,
                             facet_row_spacing=0.08,
                             color_discrete_map={"Neste cluster": COR_DESTAQUE, "Demais pontos": "#5B6B7F"},
                             category_orders={"grupo": ["Demais pontos", "Neste cluster"]}, opacity=0.8,
                             labels={"pc1": "PC1", "pc2": "PC2", "grupo": ""},
                             title=f"Clusters do K-Means (k = {k}), um painel por cluster")
            fig.update_traces(marker_size=4)
            fig.for_each_annotation(lambda anotacao: anotacao.update(text=anotacao.text.split("=", 1)[-1]))
            fig.update_layout(height=300 * int(np.ceil(k / 3)) + 100)
            mostrar(fig)
        esquerda, direita = st.columns(2)
        with esquerda:
            fig = px.scatter(pontos.assign(cluster=rotulos[k].astype(str)), x="pc1", y="pc2", color="cluster",
                             category_orders={"cluster": [str(i) for i in range(k)]}, opacity=0.7,
                             labels={"pc1": eixo_x, "pc2": eixo_y, "cluster": "Cluster"},
                             title=f"Clusters do K-Means (k = {k})")
            mostrar(fig)
        with direita:
            fig = px.scatter(pontos, x="pc1", y="pc2", color="classe", category_orders={"classe": ORDEM_NOMES_CLASSES},
                             opacity=0.7, color_discrete_sequence=CORES_CLASSES,
                             labels={"pc1": eixo_x, "pc2": eixo_y, "classe": "Classe real"},
                             title="Classes reais (ordem do IMC)")
            mostrar(fig)
        st.caption(
            f"Os dois graficos usam a mesma projecao PCA, que explica cerca de {var_exp.sum():.0f}% da variancia, "
            "entao parte da sobreposicao vem da projecao."
        )
        esquerda, direita = st.columns((1.4, 1))
        with esquerda:
            fig = px.imshow(matriz.rename(index=NOMES_CLASSES, columns=NOMES_CLASSES), text_auto=True,
                            color_continuous_scale="Blues", aspect="auto",
                            labels={"x": "Rotulo mapeado (classe majoritaria do cluster)", "y": "Classe real", "color": "Pessoas"},
                            title=f"Matriz de confusao ({matriz.shape[0]} x {matriz.shape[1]})")
            mostrar(fig)
        with direita:
            st.markdown("**Precisao e recall por classe**")
            st.dataframe(metricas.rename(index=NOMES_CLASSES).round(3), width="stretch")

    with aba_animacao:
        quadros = pd.concat([
            pontos.assign(cluster=rotulos[K_LIVRE].astype(str), passada=f"Passada 1 (k = {K_LIVRE})"),
            pontos.assign(cluster=rotulos[K_FIXO].astype(str), passada=f"Passada 2 (k = {K_FIXO})"),
        ])
        fig = px.scatter(quadros, x="pc1", y="pc2", color="cluster", animation_frame="passada",
                         category_orders={"cluster": [str(i) for i in range(K_FIXO)]}, opacity=0.7,
                         range_x=[quadros["pc1"].min() - 0.3, quadros["pc1"].max() + 0.3],
                         range_y=[quadros["pc2"].min() - 0.3, quadros["pc2"].max() + 0.3],
                         labels={"pc1": eixo_x, "pc2": eixo_y, "cluster": "Cluster", "passada": "Passada"},
                         title="Transicao da Passada 1 para a Passada 2 na mesma projecao PCA")
        fig.update_layout(height=620)
        mostrar(fig)
        st.caption("Use o botao de play ou o controle deslizante. Os numeros dos clusters nao se correspondem entre as passadas.")

    with aba_macro:
        # [IA] Claude Code - macro-classes com mapeamento por maioria e um-para-um, e clusters x meio de transporte
        st.markdown(
            "As 7 classes agrupadas em 4 macro-classes (Abaixo do Peso, Normal, Sobrepeso e Obesidade), avaliadas com os "
            f"clusters da Passada 1 (k = {K_LIVRE}). Pelo mapeamento por maioria, dois clusters recebem o rotulo Obesidade "
            "e a coluna Sobrepeso fica zerada. O mapeamento um-para-um (algoritmo hungaro) obriga cada cluster a receber "
            "uma macro-classe diferente."
        )
        y4 = y.map(MACRO_CLASSES)
        composicao = pd.crosstab(pd.Series(rotulos[K_LIVRE], name="Cluster"), y4.rename("Macro-classe"))[ORDEM_MACRO]
        linhas, colunas = linear_sum_assignment(-composicao.to_numpy())
        mapeamentos = {
            "Por maioria": composicao.idxmax(axis=1).to_dict(),
            "Um-para-um": {composicao.index[i]: ORDEM_MACRO[j] for i, j in zip(linhas, colunas)},
        }
        baseline_macro = y4.value_counts(normalize=True).max()
        resumo = []
        cols = st.columns(2)
        for coluna, (nome, mapa) in zip(cols, mapeamentos.items()):
            previsto = pd.Series(rotulos[K_LIVRE]).map(mapa)
            matriz = pd.crosstab(y4.rename("Classe real"), previsto.rename("Rotulo mapeado")).reindex(
                index=ORDEM_MACRO, columns=ORDEM_MACRO, fill_value=0
            )
            acertos = np.diag(matriz.to_numpy())
            resumo.append(pd.DataFrame({
                "mapeamento": nome,
                "macro-classe": ORDEM_MACRO,
                "precisao": acertos / np.where(matriz.sum(axis=0) > 0, matriz.sum(axis=0), np.nan),
                "recall": acertos / matriz.sum(axis=1).to_numpy(),
            }).fillna(0))
            with coluna:
                st.metric(f"Acuracia ({nome.lower()})", pct(acertos.sum() / matriz.to_numpy().sum()))
                fig = px.imshow(matriz, text_auto=True, color_continuous_scale="Blues", aspect="auto",
                                labels={"x": "Rotulo mapeado", "y": "Classe real", "color": "Pessoas"},
                                title=f"Matriz de confusao 4 x 4, {nome.lower()}")
                mostrar(fig)
        st.caption(f"Baseline (sempre Obesidade, a macro-classe mais frequente): {pct(baseline_macro)}.")
        st.dataframe(
            pd.concat(resumo).pivot(index="macro-classe", columns="mapeamento").reindex(ORDEM_MACRO).round(3),
            width="stretch",
        )
        st.markdown(
            "**Por que os clusters nao separam sobrepeso de obesidade.** A tabela cruza os clusters com o meio de "
            "transporte. Depois do One-Hot e da padronizacao, MTRANS virou 5 colunas, e as categorias raras ficaram com "
            "valores muito altos, entao o transporte domina a distancia do K-Means."
        )
        passada = st.radio("Passada", [f"Passada 1 (k = {K_LIVRE})", f"Passada 2 (k = {K_FIXO})"], horizontal=True)
        k_tab = K_LIVRE if passada.startswith("Passada 1") else K_FIXO
        st.dataframe(pd.crosstab(pd.Series(rotulos[k_tab], name="Cluster"), df["MTRANS"].rename("Transporte")),
                     width="stretch")


# ---------------------------------------------------------------- navegacao

navegacao = st.navigation([
    st.Page(pagina_especifica, title="Parte Especifica (Adult)", icon="📊", default=True),
    st.Page(pagina_comum, title="Parte Comum (Obesity)", icon="🧩"),
])
navegacao.run()

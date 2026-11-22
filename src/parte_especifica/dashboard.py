"""Dashboard interativo da Parte Específica — dataset Adult.

Execução: streamlit run src/parte_especifica/dashboard.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# [IA] Codex — apoio técnico com Streamlit, pandas e Plotly para estruturar
# o dashboard e seus filtros. O grupo deve revisar o código e dominar a
# explicação de cada visualização e decisão analítica.
ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "parte_especifica" / "adult.csv"
CORES = {"<=50K": "#4C78A8", ">50K": "#E45756"}
FAIXAS_HORAS = ["até 20", "21–39", "40", "41–50", "51+"]

st.set_page_config(
    page_title="Adult Income Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def carregar_dados(caminho: str) -> pd.DataFrame:
    """Carrega e prepara o dataset para o dashboard."""
    df = pd.read_csv(caminho)
    df["income"] = df["income"].astype(str).str.strip().str.rstrip(".")
    df["alta_renda"] = df["income"].eq(">50K")
    df["workclass"] = df["workclass"].fillna("Desconhecido")
    df["occupation"] = df["occupation"].fillna("Desconhecido")
    df["native-country"] = df["native-country"].fillna("Desconhecido")
    df["faixa_horas"] = pd.cut(
        df["hours-per-week"],
        bins=[0, 20, 39, 40, 50, float("inf")],
        labels=FAIXAS_HORAS,
        include_lowest=True,
    )
    return df


def titulo(texto: str, subtitulo: str | None = None) -> None:
    st.subheader(texto)
    if subtitulo:
        st.caption(subtitulo)


def grafico_taxa_por_categoria(
    df: pd.DataFrame, coluna: str, titulo_grafico: str, minimo: int = 0
) -> None:
    tabela = (
        df.groupby(coluna, dropna=False)["alta_renda"]
        .agg(taxa="mean", pessoas="size")
        .reset_index()
        .query("pessoas >= @minimo")
        .sort_values("taxa")
    )
    tabela["taxa_percentual"] = tabela["taxa"] * 100
    fig = px.bar(
        tabela,
        x="taxa_percentual",
        y=coluna,
        orientation="h",
        text="taxa_percentual",
        hover_data={"pessoas": ":,", "taxa_percentual": ".1f"},
        labels={"taxa_percentual": "% com renda >50K", coluna: ""},
        title=titulo_grafico,
        color_discrete_sequence=["#4C78A8"],
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(showlegend=False, margin=dict(l=10, r=55, t=55, b=10))
    st.plotly_chart(fig, use_container_width=True)


if not DATA_PATH.exists():
    st.error("Dataset não encontrado em `data/parte_especifica/adult.csv`.")
    st.code("python src/parte_especifica/download_data.py", language="powershell")
    st.stop()

df = carregar_dados(str(DATA_PATH))

st.title("📊 Adult Income Explorer")
st.write(
    "Exploração interativa da base Adult: perfis sociodemográficos, trabalho, "
    "escolaridade e faixa de renda anual."
)
st.info(
    "Leitura descritiva: os gráficos mostram associações presentes na amostra; "
    "eles não demonstram relações de causa e efeito.",
    icon="ℹ️",
)

with st.sidebar:
    st.header("Filtros")
    sexo = st.multiselect("Sexo", sorted(df["sex"].unique()), default=sorted(df["sex"].unique()))
    classes_trabalho = st.multiselect(
        "Tipo de trabalho",
        sorted(df["workclass"].unique()),
        default=sorted(df["workclass"].unique()),
    )
    faixa_idade = st.slider("Faixa de idade", 17, 90, (17, 90))
    faixa_horas = st.slider("Horas trabalhadas por semana", 1, 99, (1, 99))
    st.divider()
    st.caption("Os filtros atualizam todos os indicadores e gráficos.")

filtrado = df.loc[
    df["sex"].isin(sexo)
    & df["workclass"].isin(classes_trabalho)
    & df["age"].between(*faixa_idade)
    & df["hours-per-week"].between(*faixa_horas)
].copy()

if filtrado.empty:
    st.warning("Nenhum registro atende aos filtros atuais. Ajuste os filtros na barra lateral.")
    st.stop()

total = len(filtrado)
taxa_alta = filtrado["alta_renda"].mean()
idade_mediana = filtrado["age"].median()
horas_mediana = filtrado["hours-per-week"].median()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Pessoas selecionadas", f"{total:,}".replace(",", "."))
col2.metric("Renda >50K", f"{taxa_alta:.1%}")
col3.metric("Idade mediana", f"{idade_mediana:.0f} anos")
col4.metric("Jornada mediana", f"{horas_mediana:.0f} h/semana")

aba_visao, aba_exploracao, aba_pergunta, aba_dados = st.tabs(
    ["Visão geral", "Exploração", "Pergunta de pesquisa", "Dados"]
)

with aba_visao:
    titulo("Panorama da amostra filtrada", "A distribuição da renda orienta a leitura dos demais gráficos.")
    esquerda, direita = st.columns((1, 1.25))
    with esquerda:
        contagem = filtrado["income"].value_counts().reindex(["<=50K", ">50K"], fill_value=0).reset_index()
        contagem.columns = ["Faixa de renda", "Pessoas"]
        fig = px.bar(
            contagem,
            x="Faixa de renda",
            y="Pessoas",
            text="Pessoas",
            color="Faixa de renda",
            color_discrete_map=CORES,
            title="Distribuição da faixa de renda",
        )
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with direita:
        faixa = pd.cut(filtrado["age"], bins=[16, 25, 35, 45, 55, 65, 90], include_lowest=True)
        por_idade = (
            filtrado.assign(faixa_idade=faixa.astype(str))
            .groupby(["faixa_idade", "income"], observed=True)
            .size()
            .reset_index(name="Pessoas")
        )
        fig = px.bar(
            por_idade,
            x="faixa_idade",
            y="Pessoas",
            color="income",
            barmode="group",
            color_discrete_map=CORES,
            labels={"faixa_idade": "Faixa de idade", "income": "Renda"},
            title="Faixa de renda por grupo de idade",
        )
        fig.update_layout(margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, use_container_width=True)

with aba_exploracao:
    titulo("Exploração dos perfis", "Use os filtros para investigar grupos e comparar padrões da amostra.")
    esquerda, direita = st.columns(2)
    with esquerda:
        grafico_taxa_por_categoria(filtrado, "occupation", "Renda >50K por ocupação", minimo=100)
    with direita:
        grafico_taxa_por_categoria(filtrado, "marital-status", "Renda >50K por estado civil", minimo=100)

    esquerda, direita = st.columns(2)
    with esquerda:
        fig = px.box(
            filtrado,
            x="income",
            y="education-num",
            color="income",
            color_discrete_map=CORES,
            category_orders={"income": ["<=50K", ">50K"]},
            labels={"income": "Renda", "education-num": "Nível numérico de escolaridade"},
            title="Escolaridade por faixa de renda",
        )
        fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with direita:
        fig = px.histogram(
            filtrado,
            x="hours-per-week",
            color="income",
            barmode="overlay",
            nbins=35,
            opacity=0.65,
            color_discrete_map=CORES,
            labels={"hours-per-week": "Horas por semana", "income": "Renda"},
            title="Distribuição da jornada semanal",
        )
        fig.update_layout(margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, use_container_width=True)

with aba_pergunta:
    titulo(
        "Pergunta de pesquisa",
        "Como a escolaridade se associa à proporção de pessoas com renda anual acima de US$ 50 mil, e como as horas trabalhadas ajudam a contextualizar essa associação?",
    )
    st.caption("A resposta é descritiva e se limita aos registros atualmente selecionados pelos filtros.")

    esquerda, direita = st.columns((1.1, 1))
    with esquerda:
        taxa_educacao = (
            filtrado.groupby("education", as_index=False)["alta_renda"]
            .agg(["mean", "size"])
            .reset_index()
            .rename(columns={"mean": "taxa", "size": "Pessoas"})
            .sort_values("taxa")
        )
        taxa_educacao["Percentual"] = taxa_educacao["taxa"] * 100
        taxa_educacao["Destaque"] = taxa_educacao["Percentual"].ge(40).map({True: "40% ou mais", False: "Abaixo de 40%"})
        fig = px.bar(
            taxa_educacao,
            x="Percentual",
            y="education",
            orientation="h",
            color="Destaque",
            color_discrete_map={"40% ou mais": "#E45756", "Abaixo de 40%": "#B9C8D8"},
            hover_data={"Pessoas": ":,"},
            labels={"education": "Escolaridade", "Percentual": "% com renda >50K"},
            title="Taxa de renda >50K por escolaridade",
        )
        fig.update_layout(legend_title_text="Taxa", margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with direita:
        cruzamento = pd.crosstab(
            filtrado["education-num"], filtrado["faixa_horas"], values=filtrado["alta_renda"], aggfunc="mean"
        ).reindex(columns=FAIXAS_HORAS)
        fig = px.imshow(
            cruzamento * 100,
            aspect="auto",
            color_continuous_scale="YlOrRd",
            labels={"color": "% com renda >50K", "x": "Faixa de horas", "y": "Escolaridade (nível numérico)"},
            title="Escolaridade, jornada e renda >50K",
        )
        fig.update_layout(margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.warning(
        "Não interprete diferenças como causalidade: idade, ocupação, estado civil e outras variáveis "
        "também podem estar associadas simultaneamente à escolaridade, à jornada e à renda.",
        icon="⚠️",
    )

with aba_dados:
    titulo("Dados e transparência")
    st.write("Pré-visualização da base após a aplicação dos filtros.")
    st.dataframe(filtrado.drop(columns=["alta_renda"]), use_container_width=True, height=380)
    csv_exportacao = filtrado.drop(columns=["alta_renda"]).to_csv(index=False).encode("utf-8")
    st.download_button(
        "Baixar recorte filtrado em CSV",
        data=csv_exportacao,
        file_name="adult_filtrado.csv",
        mime="text/csv",
    )
    st.caption("Fonte: UCI Machine Learning Repository — Adult (Becker & Kohavi, 1996).")

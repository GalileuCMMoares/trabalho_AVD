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
    CORES_RENDA,
    ESCOLARIDADE,
    FAIXAS_HORAS,
    ORDEM_ESCOLARIDADE,
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
K_LIVRE, K_FIXO = 4, 7
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
        barmode="overlay",
        histnorm="percent",
        nbins=nbins,
        opacity=0.6,
        color_discrete_map=CORES_RENDA,
        category_orders={"renda": ORDEM_RENDA},
        labels={coluna: rotulo, "renda": "Faixa de renda"},
        title=titulo,
    )
    fig.update_layout(yaxis_title="% dentro de cada faixa de renda")
    mostrar(fig)


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
    fig = px.box(
        df,
        x="renda",
        y="education-num",
        color="renda",
        color_discrete_map=CORES_RENDA,
        category_orders={"renda": ORDEM_RENDA},
        labels={"renda": "Faixa de renda anual", "education-num": "Nivel de escolaridade"},
        title="Nivel de escolaridade por faixa de renda",
    )
    fig.update_yaxes(tickvals=list(ESCOLARIDADE), ticktext=ORDEM_ESCOLARIDADE)
    fig.update_layout(showlegend=False, height=540)
    mostrar(fig)


def grafico_pergunta(df: pd.DataFrame) -> None:
    tabela = taxa_por(df, "education-num").sort_values("education-num")
    tabela["escolaridade"] = tabela["education-num"].map(ESCOLARIDADE)
    tabela["grupo"] = np.where(tabela["education-num"] >= 13, "Graduacao ou mais", "Abaixo da graduacao")
    sup = df.loc[df["graduacao_ou_mais"], "alta_renda"]
    inf = df.loc[~df["graduacao_ou_mais"], "alta_renda"]
    if len(sup) and len(inf):
        titulo = (f"Com graduacao ou mais, {pct(sup.mean())} tem renda acima de US$ 50 mil<br>"
                  f"contra {pct(inf.mean())} nos niveis abaixo da graduacao")
    else:
        titulo = "Taxa de renda acima de US$ 50 mil por escolaridade"
    fig = px.bar(
        tabela,
        x="percentual",
        y="escolaridade",
        orientation="h",
        color="grupo",
        color_discrete_map={"Graduacao ou mais": COR_DESTAQUE, "Abaixo da graduacao": COR_CONTEXTO},
        category_orders={"escolaridade": ORDEM_ESCOLARIDADE, "grupo": ["Graduacao ou mais", "Abaixo da graduacao"]},
        hover_data={"pessoas": ":,", "grupo": False},
        labels={"percentual": "% com renda acima de US$ 50 mil", "escolaridade": "Escolaridade", "pessoas": "Pessoas"},
        title=titulo,
    )
    fig.update_traces(texttemplate="%{x:.0f}%", textposition="outside", cliponaxis=False)
    fig.update_layout(height=580, legend_title_text="", xaxis_showgrid=False, xaxis_range=[0, 100])
    mostrar(fig)


def grafico_mapa_calor(df: pd.DataFrame) -> None:
    faixa = df["faixa_horas"].astype(str)
    taxa = pd.crosstab(df["education-num"], faixa, values=df["alta_renda"], aggfunc="mean").reindex(columns=FAIXAS_HORAS)
    contagem = pd.crosstab(df["education-num"], faixa).reindex(index=taxa.index, columns=FAIXAS_HORAS).fillna(0)
    z = (taxa * 100).where(contagem >= MINIMO_CELULA)
    niveis = [ESCOLARIDADE[n] for n in z.index]
    texto = z.map(lambda v: "" if pd.isna(v) else f"{v:.0f}")
    fig = go.Figure(
        go.Heatmap(
            z=z.to_numpy(),
            x=FAIXAS_HORAS,
            y=niveis,
            text=texto.to_numpy(),
            texttemplate="%{text}",
            customdata=contagem.to_numpy().astype(int),
            colorscale="YlOrRd",
            zmin=0,
            zmax=100,
            hoverongaps=False,
            colorbar=dict(title="% com renda<br>acima de<br>US$ 50 mil"),
            hovertemplate="%{y}<br>Jornada %{x} horas<br>%{z:.1f}% com renda acima de US$ 50 mil"
                          "<br>%{customdata} pessoas<extra></extra>",
        )
    )
    fig.update_layout(
        title="Renda alta e mais frequente onde escolaridade e jornada sao maiores",
        xaxis_title="Horas trabalhadas por semana",
        yaxis_title="Escolaridade",
        height=580,
    )
    fig.update_yaxes(categoryorder="array", categoryarray=niveis)
    mostrar(fig)
    st.caption(f"Celulas com menos de {MINIMO_CELULA} pessoas no recorte ficam em branco para evitar percentuais instaveis.")


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


def explorador(df: pd.DataFrame) -> None:
    st.subheader("Explorar a relacao entre duas variaveis")
    st.caption("Escolha duas variaveis e o grafico se ajusta ao tipo delas. Os filtros da barra lateral continuam valendo.")
    nomes = list(VARIAVEIS)
    esquerda, direita, extra = st.columns((1, 1, 1))
    nome_a = esquerda.selectbox("Primeira variavel", nomes, index=nomes.index("Escolaridade"))
    nome_b = direita.selectbox("Segunda variavel", nomes, index=nomes.index("Horas por semana"))
    separar = extra.checkbox("Separar por faixa de renda", value=False)
    if nome_a == nome_b:
        st.info("Escolha duas variaveis diferentes.")
        return
    (col_a, tipo_a), (col_b, tipo_b) = VARIAVEIS[nome_a], VARIAVEIS[nome_b]
    separar = separar and "renda" not in (col_a, col_b)

    if tipo_a == "num" and tipo_b == "num":
        fig = px.density_heatmap(
            df, x=col_a, y=col_b, nbinsx=40, nbinsy=40, color_continuous_scale="Blues",
            facet_col="renda" if separar else None, category_orders={"renda": ORDEM_RENDA},
            labels={col_a: nome_a, col_b: nome_b, "renda": "Faixa de renda"},
            title=f"{nome_a} e {nome_b} (concentracao de pessoas)",
        )
        fig.update_coloraxes(colorbar_title="Pessoas")
        mostrar(fig)
        correlacao = df[col_a].corr(df[col_b])
        st.metric("Correlacao de Pearson", f"{correlacao:.2f}".replace(".", ","))
    elif tipo_a == "cat" and tipo_b == "cat":
        tabela = pd.crosstab(df[col_a].astype(str), df[col_b].astype(str), normalize="index") * 100
        longo = tabela.reset_index().melt(id_vars=col_a, var_name=col_b, value_name="percentual")
        ordem_a = ordem_categorias(df, col_a)
        fig = px.bar(
            longo, x="percentual", y=col_a, color=col_b, orientation="h",
            category_orders={col_a: ordem_a, col_b: ordem_categorias(df, col_b)},
            color_discrete_map=CORES_RENDA if col_b == "renda" else None,
            labels={"percentual": "% dentro de cada grupo", col_a: nome_a, col_b: nome_b},
            title=f"Composicao de {nome_b.lower()} em cada grupo de {nome_a.lower()}",
        )
        fig.update_layout(barmode="stack", height=max(400, 32 * len(ordem_a) + 160), xaxis_range=[0, 100])
        mostrar(fig)
        st.caption("Cada barra soma 100%.")
    else:
        col_cat, nome_cat, col_num, nome_num = (col_a, nome_a, col_b, nome_b) if tipo_a == "cat" else (col_b, nome_b, col_a, nome_a)
        ordem = ordem_categorias(df, col_cat)
        fig = px.box(
            df.assign(**{col_cat: df[col_cat].astype(str)}), x=col_num, y=col_cat, orientation="h",
            color="renda" if separar else None, color_discrete_map=CORES_RENDA,
            category_orders={col_cat: ordem, "renda": ORDEM_RENDA},
            labels={col_num: nome_num, col_cat: nome_cat, "renda": "Faixa de renda"},
            title=f"{nome_num} por {nome_cat.lower()}",
        )
        fig.update_layout(height=max(400, 34 * len(ordem) + 160))
        mostrar(fig)


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
    col1.metric("Pessoas selecionadas", inteiro(len(filtrado)))
    col2.metric("Renda acima de US$ 50 mil", pct(filtrado["alta_renda"].mean()))
    col3.metric("Idade mediana", f"{filtrado['age'].median():.0f} anos")
    col4.metric("Jornada mediana", f"{filtrado['hours-per-week'].median():.0f} h por semana")

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
            histograma_por_renda(filtrado, "hours-per-week", "Horas trabalhadas por semana",
                                 "Distribuicao da jornada semanal por faixa de renda", 40)
            nota("jornada")

    with aba_pergunta:
        st.subheader("Pergunta de pesquisa")
        st.caption(
            "Como a escolaridade se associa a proporcao de pessoas com renda anual acima de US$ 50 mil, "
            "e como as horas trabalhadas ajudam a contextualizar essa associacao? A resposta se limita aos registros filtrados."
        )
        esquerda, direita = st.columns((1.1, 1))
        with esquerda:
            grafico_pergunta(filtrado)
            nota("pergunta")
        with direita:
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
    pontos = pd.DataFrame({"pc1": coords[:, 0], "pc2": coords[:, 1], "classe": y})

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
        esquerda, direita = st.columns(2)
        with esquerda:
            fig = px.scatter(pontos.assign(cluster=rotulos[k].astype(str)), x="pc1", y="pc2", color="cluster",
                             category_orders={"cluster": [str(i) for i in range(k)]}, opacity=0.7,
                             labels={"pc1": eixo_x, "pc2": eixo_y, "cluster": "Cluster"},
                             title=f"Clusters do K-Means (k = {k})")
            mostrar(fig)
        with direita:
            fig = px.scatter(pontos, x="pc1", y="pc2", color="classe", category_orders={"classe": CLASSES_OBESITY},
                             opacity=0.7, color_discrete_sequence=px.colors.sequential.Plasma_r,
                             labels={"pc1": eixo_x, "pc2": eixo_y, "classe": "Classe real"},
                             title="Classes reais (NObeyesdad)")
            mostrar(fig)
        st.caption(
            f"Os dois graficos usam a mesma projecao PCA, que explica cerca de {var_exp.sum():.0f}% da variancia, "
            "entao parte da sobreposicao vem da projecao."
        )
        esquerda, direita = st.columns((1.4, 1))
        with esquerda:
            fig = px.imshow(matriz, text_auto=True, color_continuous_scale="Blues", aspect="auto",
                            labels={"x": "Rotulo mapeado (classe majoritaria do cluster)", "y": "Classe real", "color": "Pessoas"},
                            title=f"Matriz de confusao ({matriz.shape[0]} x {matriz.shape[1]})")
            mostrar(fig)
        with direita:
            st.markdown("**Precisao e recall por classe**")
            st.dataframe(metricas.round(3), width="stretch")

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

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


# [IA] Codex — estrutura técnica para carregar os dados e gerar gráficos.
# O grupo deve revisar o código e dominar as decisões analíticas apresentadas.
ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "parte_especifica" / "adult.csv"
OUTPUT_DIR = ROOT / "out" / "parte_especifica" / "visualizacoes"
PALETA_RENDA = {"<=50K": "#4C78A8", ">50K": "#E45756"}


def preparar_dados() -> pd.DataFrame:
    """Carrega o Adult e cria apenas variáveis derivadas para os gráficos."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "Dataset não encontrado. Execute primeiro: "
            "python src/parte_especifica/download_data.py"
        )

    df = pd.read_csv(DATA_PATH)
    df["income"] = df["income"].astype(str).str.strip().str.rstrip(".")
    df["alta_renda"] = df["income"].eq(">50K")
    df["faixa_horas"] = pd.cut(
        df["hours-per-week"],
        bins=[0, 20, 39, 40, 50, np.inf],
        labels=["até 20", "21–39", "40", "41–50", "51+"],
        include_lowest=True,
    )
    return df


def finalizar(ax: plt.Axes, titulo: str, xlabel: str, ylabel: str) -> None:
    ax.set_title(titulo, loc="left", fontweight="bold", pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.spines[["top", "right"]].set_visible(False)


def salvar(fig: plt.Figure, nome: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / f"{nome}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def exploratoria_1_classe(df: pd.DataFrame) -> None:
    """E1 — distribuição da classe alvo."""
    contagem = df["income"].value_counts().reindex(["<=50K", ">50K"])
    fig, ax = plt.subplots(figsize=(6.5, 4))
    barras = ax.bar(contagem.index, contagem.values, color=[PALETA_RENDA[x] for x in contagem.index])
    for barra, valor in zip(barras, contagem.values):
        ax.text(barra.get_x() + barra.get_width() / 2, valor + 500, f"{valor:,}\n({valor / len(df):.1%})", ha="center")
    ax.set_ylim(0, contagem.max() * 1.16)
    finalizar(ax, "Distribuição da faixa de renda", "Faixa de renda anual", "Número de pessoas")
    salvar(fig, "01 - Distribuição por Renda")


def exploratoria_2_idade(df: pd.DataFrame) -> None:
    """E2 — distribuição de idade separada por classe."""
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    sns.histplot(
        data=df,
        x="age",
        hue="income",
        bins=30,
        stat="percent",
        common_norm=False,
        palette=PALETA_RENDA,
        alpha=0.45,
        ax=ax,
    )
    finalizar(ax, "Distribuição de idade por faixa de renda", "Idade (anos)", "% dentro de cada faixa de renda")
    ax.legend_.set_title("Renda")
    salvar(fig, "02 - Idade por Renda")


def exploratoria_3_educacao(df: pd.DataFrame) -> None:
    """E3 — escolaridade numérica por classe, sem inferir causalidade."""
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    sns.boxplot(
        data=df,
        x="income",
        y="education-num",
        order=["<=50K", ">50K"],
        hue="income",
        palette=PALETA_RENDA,
        legend=False,
        ax=ax,
    )
    finalizar(ax, "Nível de escolaridade por faixa de renda", "Faixa de renda anual", "Nível numérico de escolaridade")
    salvar(fig, "03 - Escolaridade por Renda")


def exploratoria_4_ocupacao(df: pd.DataFrame) -> None:
    """E4 — taxa de alta renda nas ocupações mais frequentes."""
    tabela = (
        df.assign(occupation=df["occupation"].fillna("Desconhecido"))
        .groupby("occupation", as_index=False)
        .agg(taxa_alta_renda=("alta_renda", "mean"), pessoas=("alta_renda", "size"))
        .query("pessoas >= 300")
        .sort_values("taxa_alta_renda")
    )
    fig, ax = plt.subplots(figsize=(8.5, 6))
    ax.barh(tabela["occupation"], tabela["taxa_alta_renda"] * 100, color="#4C78A8")
    finalizar(ax, "Taxa de renda acima de US$ 50 mil por ocupação", "% com renda >50K", "Ocupação")
    ax.set_xlim(0, max(55, tabela["taxa_alta_renda"].max() * 115))
    salvar(fig, "04 - Renda por ocupação")


def explanatoria_1_pergunta_pesquisa(df: pd.DataFrame) -> None:
    """X1 — responde diretamente à pergunta de pesquisa proposta."""
    tabela = (
        df.groupby("education", as_index=False)
        .agg(taxa_alta_renda=("alta_renda", "mean"), pessoas=("alta_renda", "size"))
        .sort_values("taxa_alta_renda")
    )
    fig, ax = plt.subplots(figsize=(9, 6.5))
    cores = ["#E45756" if valor >= 0.40 else "#B9C8D8" for valor in tabela["taxa_alta_renda"]]
    barras = ax.barh(tabela["education"], tabela["taxa_alta_renda"] * 100, color=cores)
    for barra, valor in zip(barras, tabela["taxa_alta_renda"]):
        ax.text(valor * 100 + 0.8, barra.get_y() + barra.get_height() / 2, f"{valor:.0%}", va="center", fontsize=9)
    finalizar(
        ax,
        "A taxa de renda >50K aumenta nos níveis mais altos de escolaridade",
        "% de pessoas com renda >50K",
        "Escolaridade",
    )
    ax.set_xlim(0, min(100, tabela["taxa_alta_renda"].max() * 100 + 12))
    ax.text(0, -0.14, "Vermelho: níveis com taxa igual ou superior a 40%. Associação descritiva; não demonstra causalidade.", transform=ax.transAxes, fontsize=8.5)
    salvar(fig, "05 - Pergunta por escolaridade")


def explanatoria_2_horas_escolaridade(df: pd.DataFrame) -> None:
    """X2 — comparação multivariada para complementar a narrativa."""
    tabela = (
        df.groupby(["education-num", "faixa_horas"], observed=False)["alta_renda"]
        .mean()
        .mul(100)
        .unstack()
    )
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        tabela,
        cmap="YlOrRd",
        vmin=0,
        vmax=70,
        annot=True,
        fmt=".0f",
        cbar_kws={"label": "% com renda >50K"},
        ax=ax,
    )
    finalizar(ax, "Renda alta é mais frequente onde escolaridade e jornada são maiores", "Faixa de horas trabalhadas por semana", "Nível numérico de escolaridade")
    ax.text(0, -0.14, "Células mostram a proporção de pessoas com renda >50K em cada combinação.", transform=ax.transAxes, fontsize=8.5)
    salvar(fig, "06 - Escolaridade por Horas")


def main() -> None:
    sns.set_theme(style="whitegrid", context="notebook")
    df = preparar_dados()
    exploratoria_1_classe(df)
    exploratoria_2_idade(df)
    exploratoria_3_educacao(df)
    exploratoria_4_ocupacao(df)
    explanatoria_1_pergunta_pesquisa(df)
    explanatoria_2_horas_escolaridade(df)
    print(f"Seis gráficos salvos em: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

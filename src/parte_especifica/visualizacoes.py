from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.ticker import FuncFormatter

from traducoes import (
    COR_CONTEXTO,
    COR_DESTAQUE,
    CORES_RENDA,
    ESCOLARIDADE,
    FAIXAS_HORAS,
    ORDEM_ESCOLARIDADE,
    ORDEM_ESCOLARIDADE_AGRUPADA,
    ORDEM_CODIGOS_ESCOLARIDADE,
    ORDEM_RENDA,
    CORES_ESCOLARIDADE_AGRUPADA,
    ROTULOS_CURTOS_AGRUPADA,
    inteiro,
    pct,
    preparar_adult,
)

# [IA] Codex - estrutura tecnica para carregar os dados e gerar os graficos
# [IA] Claude Code - rotulos em portugues, escolaridade na ordem dos niveis, mascara de celulas pequenas
# no mapa de calor, escala de cor completa e numeros no padrao brasileiro
ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "parte_especifica" / "adult.csv"
OUTPUT_DIR = ROOT / "out" / "parte_especifica" / "visualizacoes"
MINIMO_OCUPACAO = 100
MINIMO_CELULA = 30
MILHAR = FuncFormatter(lambda v, _: inteiro(v))


def preparar_dados() -> pd.DataFrame:
    """Carrega o Adult e cria as colunas traduzidas usadas nos graficos."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "Dataset nao encontrado. Execute primeiro, python src/parte_especifica/download_data.py"
        )
    return preparar_adult(pd.read_csv(DATA_PATH))


def finalizar(ax: plt.Axes, titulo: str, xlabel: str, ylabel: str) -> None:
    ax.set_title(titulo, loc="left", fontweight="bold", pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.spines[["top", "right"]].set_visible(False)


def rodape(ax: plt.Axes, texto: str, y: float = -0.14) -> None:
    ax.text(0, y, texto, transform=ax.transAxes, fontsize=8.5, color="#555555")


def salvar(fig: plt.Figure, nome: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / f"{nome}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def exploratoria_1_classe(df: pd.DataFrame) -> None:
    """E1, distribuicao da classe alvo."""
    contagem = df["renda"].value_counts().reindex(ORDEM_RENDA)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    barras = ax.bar(contagem.index, contagem.values, color=[CORES_RENDA[x] for x in contagem.index])
    for barra, valor in zip(barras, contagem.values):
        ax.text(barra.get_x() + barra.get_width() / 2, valor + 500,
                f"{inteiro(valor)}\n({pct(valor / len(df))})", ha="center")
    ax.set_ylim(0, contagem.max() * 1.18)
    ax.yaxis.set_major_formatter(MILHAR)
    finalizar(ax, "Distribuicao da faixa de renda", "Faixa de renda anual", "Numero de pessoas")
    salvar(fig, "01 - Distribuição por Renda")


def exploratoria_2_idade(df: pd.DataFrame) -> None:
    """E2, distribuicao de idade dentro de cada faixa de renda."""
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    sns.histplot(
        data=df,
        x="age",
        hue="renda",
        hue_order=ORDEM_RENDA,
        bins=30,
        stat="percent",
        common_norm=False,
        palette=CORES_RENDA,
        alpha=0.45,
        ax=ax,
    )
    finalizar(ax, "Distribuicao de idade por faixa de renda", "Idade (anos)", "% dentro de cada faixa de renda")
    ax.legend_.set_title("Faixa de renda")
    salvar(fig, "02 - Idade por Renda")


def exploratoria_3_educacao(df: pd.DataFrame) -> None:
    """E3, nivel de escolaridade por faixa de renda, sem inferir causalidade."""
    tabela = pd.crosstab(df["escolaridade_agrupada"], df["renda"], normalize="index").reindex(
        index=ORDEM_ESCOLARIDADE_AGRUPADA, columns=ORDEM_RENDA, fill_value=0
    ).fillna(0) * 100
    fig, ax = plt.subplots(figsize=(9, 7))
    tabela.plot.barh(stacked=True, ax=ax, color=[CORES_RENDA[renda] for renda in ORDEM_RENDA])
    ax.set_xlim(0, 100)
    ax.legend(title="Faixa de renda anual", loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False)
    finalizar(ax, "Faixa de renda em cada nivel de escolaridade", "% de pessoas no nivel", "Escolaridade agrupada (EUA)")
    rodape(ax, "Categorias dos EUA; associate degree nao representa equivalencia formal com diploma brasileiro.", y=-0.28)
    salvar(fig, "03 - Escolaridade por Renda")


def exploratoria_4_ocupacao(df: pd.DataFrame) -> None:
    """E4, taxa de alta renda nas ocupacoes com pelo menos 100 pessoas."""
    tabela = (
        df.groupby("ocupacao", as_index=False)
        .agg(taxa_alta_renda=("alta_renda", "mean"), pessoas=("alta_renda", "size"))
        .query("pessoas >= @MINIMO_OCUPACAO")
        .sort_values("taxa_alta_renda")
    )
    fig, ax = plt.subplots(figsize=(8.5, 6))
    barras = ax.barh(tabela["ocupacao"], tabela["taxa_alta_renda"] * 100, color=CORES_RENDA["Ate US$ 50 mil"])
    for barra, valor in zip(barras, tabela["taxa_alta_renda"]):
        ax.text(valor * 100 + 0.6, barra.get_y() + barra.get_height() / 2, pct(valor), va="center", fontsize=8.5)
    finalizar(ax, "Taxa de renda acima de US$ 50 mil por ocupacao", "% com renda acima de US$ 50 mil", "Ocupacao")
    ax.set_xlim(0, max(55, tabela["taxa_alta_renda"].max() * 115))
    rodape(ax, f"Ocupacoes com pelo menos {MINIMO_OCUPACAO} pessoas.", y=-0.17)
    salvar(fig, "04 - Renda por ocupação")


def explanatoria_1_pergunta_pesquisa(df: pd.DataFrame) -> None:
    """X1, responde diretamente a pergunta de pesquisa."""
    tabela = (
        df.groupby("escolaridade_agrupada", as_index=False, observed=True)
        .agg(taxa_alta_renda=("alta_renda", "mean"), pessoas=("alta_renda", "size"))
        .sort_values("escolaridade_agrupada")
    )
    destaque = tabela["escolaridade_agrupada"] == ORDEM_ESCOLARIDADE_AGRUPADA[-1]
    taxa_sup = df.loc[df["graduacao_ou_mais"], "alta_renda"].mean()
    taxa_inf = df.loc[~df["graduacao_ou_mais"], "alta_renda"].mean()

    fig, ax = plt.subplots(figsize=(9, 6.5))
    cores = np.where(destaque, COR_DESTAQUE, COR_CONTEXTO)
    barras = ax.barh(tabela["escolaridade_agrupada"].astype(str), tabela["taxa_alta_renda"] * 100, color=cores)
    for barra, valor, forte in zip(barras, tabela["taxa_alta_renda"], destaque):
        ax.text(valor * 100 + 0.8, barra.get_y() + barra.get_height() / 2, pct(valor, 0), va="center",
                fontsize=9, fontweight="bold" if forte else "normal")
    finalizar(
        ax,
        f"Com bacharelado ou mais, {pct(taxa_sup, 0)} tem renda acima de US$ 50 mil, contra {pct(taxa_inf, 0)} abaixo",
        "% de pessoas com renda acima de US$ 50 mil",
        "Escolaridade",
    )
    ax.grid(False)
    ax.set_xlim(0, 100)
    rodape(
        ax,
        f"Coral, bacharelado ou mais ({pct(taxa_sup)} no conjunto). Cinza azulado, grupos abaixo do bacharelado "
        f"({pct(taxa_inf)}). Associacao descritiva, nao demonstra causalidade.",
    )
    salvar(fig, "05 - Pergunta por escolaridade")


def explanatoria_2_horas_escolaridade(df: pd.DataFrame) -> None:
    """X2, taxa de renda alta ao longo das faixas de horas, uma linha por grupo de escolaridade."""
    # [IA] Claude Code - troca do mapa de calor por linhas, pedida no feedback da professora
    df = df.assign(faixa=df["faixa_horas"].astype(str))
    taxa = pd.crosstab(df["escolaridade_agrupada"], df["faixa"], values=df["alta_renda"], aggfunc="mean")
    contagem = pd.crosstab(df["escolaridade_agrupada"], df["faixa"])
    taxa = taxa.reindex(index=ORDEM_ESCOLARIDADE_AGRUPADA, columns=FAIXAS_HORAS) * 100
    contagem = contagem.reindex(index=taxa.index, columns=FAIXAS_HORAS).fillna(0)
    taxa = taxa.where(contagem >= MINIMO_CELULA)

    fig, ax = plt.subplots(figsize=(10, 6.5))
    x = np.arange(len(FAIXAS_HORAS))
    # rotulo no fim de cada linha, afastando rotulos que ficariam colados (diferenca menor que 4 pontos)
    finais = taxa["51 ou mais"].sort_values()
    posicoes, anterior = {}, -10.0
    for grupo, valor in finais.items():
        anterior = max(valor, anterior + 4)
        posicoes[grupo] = anterior
    for grupo in ORDEM_ESCOLARIDADE_AGRUPADA:
        valores = taxa.loc[grupo].to_numpy()
        forte = grupo == ORDEM_ESCOLARIDADE_AGRUPADA[-1]
        ax.plot(x, valores, marker="o", color=CORES_ESCOLARIDADE_AGRUPADA[grupo], linewidth=3 if forte else 2)
        ax.text(x[-1] + 0.12, posicoes[grupo], f"{ROTULOS_CURTOS_AGRUPADA[grupo]} ({pct(valores[-1] / 100, 0)})",
                va="center", fontsize=9, color="#333333", fontweight="bold" if forte else "normal")
    bach_40 = taxa.loc[ORDEM_ESCOLARIDADE_AGRUPADA[-1], "40"]
    ax.annotate(f"Bacharelado com 40 h: {pct(bach_40 / 100, 0)}, acima de qualquer\noutro grupo mesmo com 51 h ou mais", xy=(2, bach_40), xytext=(0.1, bach_40 + 14),
                arrowprops=dict(arrowstyle="-", color="#777777"), fontsize=9, color="#333333")
    ax.set_xticks(x, FAIXAS_HORAS)
    ax.set_ylim(0, 75)
    ax.set_xlim(-0.2, len(FAIXAS_HORAS) + 0.6)
    ax.grid(axis="x", visible=False)
    finalizar(
        ax,
        "Jornada longa nao compensa escolaridade baixa",
        "Horas trabalhadas por semana",
        "% com renda acima de US$ 50 mil",
    )
    rodape(
        ax,
        f"Cada ponto e a % de pessoas com renda acima de US$ 50 mil no grupo e na faixa de horas. Pontos com menos "
        f"de {MINIMO_CELULA} pessoas sao omitidos. Associacao descritiva, nao demonstra causalidade.",
        y=-0.14,
    )
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
    print(f"Seis graficos salvos em {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

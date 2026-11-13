"""Gera tabelas descritivas iniciais para a EDA do Adult.

Este script produz tabelas para inspeção pelo grupo. Ele não escolhe gráficos,
não interpreta os resultados e não recomenda tratamento para os candidatos a outlier.
"""

from pathlib import Path

import pandas as pd

# [IA] Codex - apoio técnico com pandas para produzir tabelas de estrutura,
# distribuições, relações descritivas e candidatos a outliers; interpretações
# e decisões ficam a cargo dos integrantes.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "parte_especifica" / "adult.csv"
OUTPUT_DIR = PROJECT_ROOT / "out" / "parte_especifica" / "eda"
TARGET = "income"


def save_schema_table(data: pd.DataFrame) -> None:
    table = pd.DataFrame(
        {
            "coluna": data.columns,
            "tipo": [str(data[column].dtype) for column in data.columns],
            "linhas_preenchidas": [int(data[column].notna().sum()) for column in data.columns],
            "valores_ausentes": [int(data[column].isna().sum()) for column in data.columns],
            "percentual_ausente": [
                round(float(data[column].isna().mean() * 100), 2)
                for column in data.columns
            ],
            "valores_unicos": [int(data[column].nunique(dropna=True)) for column in data.columns],
        }
    )
    table.to_csv(OUTPUT_DIR / "estrutura_e_ausencias.csv", index=False)


def save_numeric_summary(data: pd.DataFrame, numeric_columns: list[str]) -> None:
    summary = data[numeric_columns].describe(
        percentiles=[0.25, 0.5, 0.75, 0.9, 0.95]
    ).transpose()
    summary.to_csv(OUTPUT_DIR / "resumo_numerico.csv")


def save_categorical_frequencies(
    data: pd.DataFrame, categorical_columns: list[str]
) -> None:
    tables = []
    for column in categorical_columns:
        counts = data[column].value_counts(dropna=False)
        table = counts.rename_axis("valor").reset_index(name="contagem")
        table["variavel"] = column
        table["proporcao"] = table["contagem"] / len(data)
        tables.append(table[["variavel", "valor", "contagem", "proporcao"]])

    if tables:
        pd.concat(tables, ignore_index=True).to_csv(
            OUTPUT_DIR / "frequencias_categoricas.csv", index=False
        )


def save_numeric_relations(
    data: pd.DataFrame, numeric_columns: list[str]
) -> None:
    summary = data.groupby(TARGET, dropna=False)[numeric_columns].agg(
        ["count", "mean", "median", "std"]
    )
    summary.columns = [
        f"{column}_{statistic}" for column, statistic in summary.columns
    ]
    summary.reset_index().to_csv(
        OUTPUT_DIR / "resumo_numerico_por_classe.csv", index=False
    )


def save_categorical_relations(
    data: pd.DataFrame, categorical_columns: list[str]
) -> None:
    tables = []
    target = data[TARGET].astype("string").fillna("[AUSENTE]")
    for column in categorical_columns:
        if column == TARGET:
            continue
        values = data[column].astype("string").fillna("[AUSENTE]")
        table = pd.crosstab(values, target, dropna=False).reset_index()
        table = table.rename(columns={column: "categoria"})
        table.insert(0, "variavel", column)
        tables.append(table)

    if tables:
        pd.concat(tables, ignore_index=True).to_csv(
            OUTPUT_DIR / "cruzamentos_categoricos_por_classe.csv", index=False
        )


def save_iqr_candidates(data: pd.DataFrame, numeric_columns: list[str]) -> None:
    rows = []
    for column in numeric_columns:
        series = data[column].dropna()
        q1 = float(series.quantile(0.25))
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        candidate_count = int(
            ((series < lower_bound) | (series > upper_bound)).sum()
        )
        rows.append(
            {
                "variavel": column,
                "q1": q1,
                "q3": q3,
                "limite_inferior_iqr": lower_bound,
                "limite_superior_iqr": upper_bound,
                "candidatos_contagem": candidate_count,
                "candidatos_percentual": (
                    round(candidate_count / len(series) * 100, 2)
                    if len(series)
                    else 0.0
                ),
            }
        )

    pd.DataFrame(rows).to_csv(
        OUTPUT_DIR / "candidatos_outliers_iqr.csv", index=False
    )


def main() -> None:
    if not DATA_PATH.exists():
        raise SystemExit(
            "Dataset não encontrado. Execute primeiro: "
            "python src/parte_especifica/download_data.py"
        )

    data = pd.read_csv(DATA_PATH)
    if TARGET not in data.columns:
        raise SystemExit(f"A coluna alvo obrigatória {TARGET!r} não foi encontrada.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    numeric_columns = data.select_dtypes(include="number").columns.tolist()
    categorical_columns = data.select_dtypes(
        include=["object", "string", "category"]
    ).columns.tolist()

    save_schema_table(data)
    save_numeric_summary(data, numeric_columns)
    save_categorical_frequencies(data, categorical_columns)
    save_numeric_relations(data, numeric_columns)
    save_categorical_relations(data, categorical_columns)
    save_iqr_candidates(data, numeric_columns)

    print(f"Tabelas descritivas salvas em: {OUTPUT_DIR}")
    print("Revise os dados e escreva as interpretações com o grupo.")


if __name__ == "__main__":
    main()

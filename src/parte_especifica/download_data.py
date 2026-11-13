"""Baixa e prepara o dataset Adult a partir do pacote oficial do UCI."""

from io import BytesIO, TextIOWrapper
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile

import pandas as pd

# [IA] Codex - apoio técnico para baixar e ler os arquivos com Python e pandas.
UCI_ZIP_URL = "https://archive.ics.uci.edu/static/public/2/adult.zip"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = PROJECT_ROOT / "data" / "parte_especifica" / "adult.csv"

COLUMNS = [
    "age",
    "workclass",
    "fnlwgt",
    "education",
    "education-num",
    "marital-status",
    "occupation",
    "relationship",
    "race",
    "sex",
    "capital-gain",
    "capital-loss",
    "hours-per-week",
    "native-country",
    "income",
]


def read_member(archive: ZipFile, member_name: str) -> pd.DataFrame:
    """Lê um arquivo de dados do pacote UCI sem inferir uma linha de cabeçalho."""
    with archive.open(member_name) as binary_file:
        text_file = TextIOWrapper(binary_file, encoding="utf-8")
        frame = pd.read_csv(
            text_file,
            header=None,
            names=COLUMNS,
            skiprows=1 if member_name == "adult.test" else 0,
            skipinitialspace=True,
            na_values=["?"],
        )

    text_columns = frame.select_dtypes(include=["object", "string"]).columns
    for column in text_columns:
        frame[column] = frame[column].str.strip()

    # O arquivo adult.test marca as classes com um ponto final.
    frame["income"] = frame["income"].str.rstrip(".")
    return frame


def main() -> None:
    request = Request(UCI_ZIP_URL, headers={"User-Agent": "AVD-Adult-Project/1.0"})
    with urlopen(request, timeout=60) as response:
        archive_bytes = response.read()

    with ZipFile(BytesIO(archive_bytes)) as archive:
        train = read_member(archive, "adult.data")
        test = read_member(archive, "adult.test")

    adult = pd.concat([train, test], ignore_index=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    adult.to_csv(OUTPUT_PATH, index=False)
    print(f"Arquivo salvo em: {OUTPUT_PATH}")
    print(f"Linhas carregadas: {len(adult)}")


if __name__ == "__main__":
    main()

import re
from collections import Counter
from copy import deepcopy
from pathlib import Path

import pandas as pd

from config import parameters
from logs_setup import logging
from modules.data.clean.contact_analysis import (
    clean_df_ofsc_capacity,
    clean_df_residential_plant,
)
from modules.data.clean.utils import CleanDataFrame
from modules.data.operations import (
    join_by_sales_advisor,
    normalize_date,
    read_excel,
)

CONTACT_ANALYSIS = parameters.CONTACT_ANALYSIS
COLUMNS_TO_RESERVE = parameters.COLUMNS_TO_RESERVE[CONTACT_ANALYSIS]


def clean_data(
    df_residential_plant: pd.DataFrame,
    files_path: list[Path],
) -> pd.DataFrame:
    NEW_RESIDENTIAL_PLANT_COLUMNS: list[str] = []
    dfs_residential_plant: list[pd.DataFrame] = []
    dfs_ofsc_capacity: list[pd.DataFrame] = []

    logging(
        message=f"Iniciando limpieza: {parameters.RESIDENTIAL_PLANT_PATH}",
        level="INFO",
    )

    for file_path in files_path:
        RESIDENTIAL_PLANT_COLUMNS = deepcopy(COLUMNS_TO_RESERVE["residential_plant"])

        logging(message=f"Iniciando limpieza: {file_path}", level="INFO")

        # Iniciamos a limpiar OFS capacidades
        df_ofsc_capacity = read_excel(path=file_path, sheet=0)
        df_ofsc_capacity = clean_df_ofsc_capacity(df=df_ofsc_capacity)

        if df_ofsc_capacity.empty:
            continue

        # Iniciamos a limpiar planta residencial
        df_residential_plant_copy = df_residential_plant.copy()
        df_residential_plant_copy = clean_df_residential_plant(
            df_ofsc_capacity=df_ofsc_capacity,
            df=df_residential_plant_copy,
        )

        # Renombramos columnas de planta residencial
        df_residential_plant_copy.rename(
            columns={"NOMBRE": "Asesor comercial"},
            inplace=True,
        )

        index = 0

        for campo in COLUMNS_TO_RESERVE["residential_plant"]:
            if campo == "NOMBRE":
                break

            index = index + 1

        RESIDENTIAL_PLANT_COLUMNS.pop(index)
        RESIDENTIAL_PLANT_COLUMNS.append("Asesor comercial")

        if not NEW_RESIDENTIAL_PLANT_COLUMNS:
            NEW_RESIDENTIAL_PLANT_COLUMNS.extend(RESIDENTIAL_PLANT_COLUMNS)

        dfs_ofsc_capacity.append(df_ofsc_capacity)
        dfs_residential_plant.append(df_residential_plant_copy)

    df_ofsc = pd.concat(objs=dfs_ofsc_capacity, ignore_index=True)
    df_ofsc = normalize_date(
        df=df_ofsc,
        column="Fecha",
        input_format="dd/mm/yy",
    )

    # Unimos OFSC y Planta residencial en uno solo
    logging(message="Uniendo OFSC y Planta Residencial...", level="INFO")

    df_residential_plant = pd.concat(objs=dfs_residential_plant, ignore_index=True)

    df_residential_plant = CleanDataFrame.drop_duplicate_rows_by_column(
        df=df_residential_plant,
        column="Asesor comercial",
    )

    df_output = join_by_sales_advisor(
        df_dictionary=df_residential_plant,
        df=df_ofsc,
    )
    df_output.rename(
        columns=parameters.FINAL_COLUMNS[CONTACT_ANALYSIS],
        inplace=True,
    )

    logging(message="Limpieza completada.\n", level="INFO")

    return df_output


def __clean_phone(value: str) -> str:
    if pd.isna(value):
        return "0"
    if isinstance(value, float):
        value = str(value)
        value = value.split(".")[0]
    if value.lower() in {"", "nan", "none"}:
        return "0"

    value = value.strip()

    if value == "":
        return "0"

    value = re.sub(r"\D", "", value)

    return value if value != "" else "0"


def data_transformation(df: pd.DataFrame) -> pd.DataFrame:
    def compute_phone_metrics(row: pd.Series) -> pd.Series:
        columns = [
            "Telefono dos del cliente",
            "Teléfono 3",
            "Celuar del contacto",
        ]

        phones = [__clean_phone(row[col]) for col in columns]

        valid_phones = [p for p in phones if p != "0"]

        counter = Counter(valid_phones)

        # Cantidad de números únicos
        unique_phone_count = len(counter)

        # Cantidad de números repetidos
        repeated_phone_count = sum(1 for count in counter.values() if count > 1)

        # Cantidad de faltantes
        empty_phone_count = phones.count("0")

        row["Cantidad de Números Únicos"] = unique_phone_count
        row["Cantidad de Números Faltantes"] = empty_phone_count
        row["Cantida de Números Repetidos"] = repeated_phone_count

        return row

    df["Cantidad de Números Únicos"] = "0"
    df["Cantidad de Números Faltantes"] = "0"
    df["Cantida de Números Repetidos"] = "0"

    df = df.apply(compute_phone_metrics, axis=1)  # type: ignore

    return df

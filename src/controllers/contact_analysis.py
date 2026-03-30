import re
from collections import Counter

import pandas as pd

from config import parameters
from data.clean.contact_analysis import (
    clean_df_ofsc_capacity,
    clean_df_residential_plant,
)
from data.clean.manager import CleanDataFrame
from data.operations import (
    join_by_sales_advisor,
    normalize_date,
)
from logs_setup import logging

CONTACT_ANALYSIS = parameters.CONTACT_ANALYSIS
COLUMNS_TO_RESERVE = parameters.COLUMNS_TO_RESERVE[CONTACT_ANALYSIS]


def clean_data(
    df_residential_plant: pd.DataFrame,
    dfs_ofsc_capacity: list[pd.DataFrame],
) -> pd.DataFrame:
    cleaned_dfs_residential_plant: list[pd.DataFrame] = []
    cleaned_dfs_ofsc_capacity: list[pd.DataFrame] = []

    for df_ofsc_capacity in dfs_ofsc_capacity:
        logging(
            message=f"Iniciando limpieza: {df_ofsc_capacity.attrs['path']}",
            level="INFO",
        )

        df_ofsc_capacity_copy = df_ofsc_capacity.copy()
        df_ofsc_capacity_copy = clean_df_ofsc_capacity(df=df_ofsc_capacity_copy)

        if df_ofsc_capacity.empty:
            continue

        # Iniciamos a limpiar planta residencial
        df_residential_plant_copy = df_residential_plant.copy()
        df_residential_plant_copy = clean_df_residential_plant(
            df_ofsc_capacity=df_ofsc_capacity_copy,
            df=df_residential_plant_copy,
        )

        # Renombramos columnas de planta residencial
        df_residential_plant_copy.rename(
            columns={"NOMBRE": "Asesor comercial"},
            inplace=True,
        )

        cleaned_dfs_ofsc_capacity.append(df_ofsc_capacity_copy)
        cleaned_dfs_residential_plant.append(df_residential_plant_copy)

    cleaned_df_ofsc_capacity = pd.concat(
        objs=cleaned_dfs_ofsc_capacity,
        ignore_index=True,
    )
    cleaned_df_ofsc_capacity = normalize_date(
        df=cleaned_df_ofsc_capacity,
        column="Fecha",
        input_format="dd/mm/yy",
    )

    # Unimos OFSC y Planta residencial en uno solo
    logging(message="Uniendo OFSC y Planta Residencial...", level="INFO")

    cleaned_df_residential_plant = pd.concat(
        objs=cleaned_dfs_residential_plant,
        ignore_index=True,
    )

    cleaned_df_residential_plant = CleanDataFrame.drop_duplicate_rows_by_column(
        df=cleaned_df_residential_plant,
        column="Asesor comercial",
    )

    df_output = join_by_sales_advisor(
        df_dictionary=cleaned_df_residential_plant,
        df=cleaned_df_ofsc_capacity,
    )
    df_output.rename(
        columns=parameters.FINAL_COLUMNS[CONTACT_ANALYSIS],
        inplace=True,
    )

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

import re
from collections import Counter

import pandas as pd

from config import parameters
from logs_setup import logging
from operations.data_frame import (
    complete_data,
    create_file,
    drop_duplicate_rows_by_column,
    filter_df,
    normalize_date,
)

CONTACT_ANALYSIS = parameters.CONTACT_ANALYSIS
FILTERS = parameters.FILTERS[CONTACT_ANALYSIS]
FINAL_COLUMNS = parameters.FINAL_COLUMNS[CONTACT_ANALYSIS]


def __prepare_df_capacity(df_capacity: pd.DataFrame) -> pd.DataFrame:

    message = f"Iniciando limpieza: {df_capacity.attrs['file_path']}"
    logging(message=message, level="INFO")

    # Filtramos para eliminar filas que no necesitamos de df_capacity
    cleaned_df_capacity = filter_df(
        filters=FILTERS["capacity_file"],
        df=df_capacity,
    )

    return cleaned_df_capacity


def __prepare_df_residential_plant(
    df_residential_plant: pd.DataFrame,
    df_capacity: pd.DataFrame,
) -> pd.DataFrame:

    # Filtramos para eliminar filas que no necesitamos de df_residential_plant
    sellers = df_capacity["Asesor comercial"].unique().tolist()
    cleaned_df_residential_plant = filter_df(
        filters={"include": {"NOMBRE": sellers}},
        df=df_residential_plant,
    )

    # Removemos filas duplicadas que no necesitamos de df_residential_plant
    # Para quedarnos solamente con los asesores comerciales únicos
    cleaned_df_residential_plant = drop_duplicate_rows_by_column(
        df=cleaned_df_residential_plant,
        column="NOMBRE",
    )

    return cleaned_df_residential_plant


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


def __data_transformation(df: pd.DataFrame) -> pd.DataFrame:

    def __compute_phone_metrics(row: pd.Series) -> pd.Series:
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

    df = df.apply(__compute_phone_metrics, axis=1)  # type: ignore

    return df


def run(df_residential_plant: pd.DataFrame, dfs_capacity: list[pd.DataFrame]) -> None:

    message = f"Iniciando limpieza de los datos para el {CONTACT_ANALYSIS}"
    logging(message=message, level="INFO")

    cleaned_dfs_capacity: list[pd.DataFrame] = []

    for df_capacity in dfs_capacity:
        cleaned_df_capacity = __prepare_df_capacity(df_capacity=df_capacity.copy())

        if cleaned_df_capacity.empty:
            continue

        cleaned_df_residential_plant = __prepare_df_residential_plant(
            df_residential_plant=df_residential_plant.copy(),
            df_capacity=cleaned_df_capacity,
        )

        # Renombramos una columna de cleaned_df_residential_plant
        # Para completar los datos de cleaned_df_capacity
        cleaned_df_residential_plant.rename(
            columns={"NOMBRE": "Asesor comercial"},
            inplace=True,
        )
        cleaned_df_capacity["GV-Especialista"] = None
        cleaned_df_capacity["GV-Descripcion"] = None
        cleaned_df_capacity["JEFE 1 CANAL REGIONAL"] = None
        cleaned_df_capacity["CANAL2"] = None
        cleaned_df_capacity = complete_data(
            df_dictionary=cleaned_df_residential_plant,
            df=cleaned_df_capacity,
            column="Asesor comercial",
            key_match="contains",
        )

        cleaned_dfs_capacity.append(cleaned_df_capacity)

    # Unimos todos los dfs del área de capacidades en uno solo
    df_output = pd.concat(
        objs=cleaned_dfs_capacity,
        ignore_index=True,
    )
    df_output = normalize_date(
        df=df_output,
        column="Fecha",
        input_format="dd/mm/yy",
    )

    df_output = __data_transformation(df=df_output)

    # Renombramos los encabezados de df_output
    df_output.rename(columns=FINAL_COLUMNS, inplace=True)

    message = f"Creando archivo final: {parameters.CONTACT_ANALYSIS_FILE_PATH}"
    logging(message=message, level="INFO")

    create_file(df=df_output, path=parameters.CONTACT_ANALYSIS_FILE_PATH)

    logging(message="Limpieza completada", level="INFO")

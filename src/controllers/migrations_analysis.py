import pandas as pd

from config import parameters
from logs_setup import logging
from operations.data_frame import create_file, drop_columns, reorder_columns

MIGRATIONS_ANALYSIS = parameters.MIGRATIONS_ANALYSIS
COLUMNS_TO_RESERVE = parameters.COLUMNS_TO_RESERVE[MIGRATIONS_ANALYSIS]
COLUMN_ORDER = parameters.COLUMN_ORDER[MIGRATIONS_ANALYSIS]
FINAL_COLUMNS = parameters.FINAL_COLUMNS[MIGRATIONS_ANALYSIS]


def __prepare_df_gpon(df_gpon: pd.DataFrame) -> pd.DataFrame:

    message = f"Iniciando limpieza: {df_gpon.attrs['file_path']}"
    logging(message=message, level="INFO")

    # Removemos columnas que no necesitamos de df_gpon
    cleaned_df_gpon = drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["gpon_file"],
        df=df_gpon,
    )

    # Creamos columnas faltantes
    cleaned_df_gpon["Tipificación"] = None
    cleaned_df_gpon["Nota"] = "NO REQUIERE"
    cleaned_df_gpon["Cronograma Desmonte Regional"] = "NO APLICA"
    cleaned_df_gpon["Cronograma Desmonte Transversal"] = "NO APLICA"
    cleaned_df_gpon["Tipo de Red"] = "GPON"

    # Renombramos columnas de planta residencial
    cleaned_df_gpon.rename(
        columns=FINAL_COLUMNS["gpon_file"],
        inplace=True,
    )

    return cleaned_df_gpon


def __prepare_df_brownfield(df_brownfield: pd.DataFrame) -> pd.DataFrame:

    message = f"Iniciando limpieza: {df_brownfield.attrs['file_path']}"
    logging(message=message, level="INFO")

    # Removemos columnas que no necesitamos de df_brownfield
    cleaned_df_brownfield = drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["brownfield_file"],
        df=df_brownfield,
    )

    # Creamos columnas faltantes
    cleaned_df_brownfield["Tipo de Red"] = "HFC"
    cleaned_df_brownfield["Código"] = "NO REQUIERE"

    # Renombramos columnas de planta residencial
    cleaned_df_brownfield.rename(
        columns=FINAL_COLUMNS["brownfield_file"],
        inplace=True,
    )

    return cleaned_df_brownfield


def run(df_gpon: pd.DataFrame, df_brownfield: pd.DataFrame) -> None:

    # Iniciamos proceso de limpieza
    message = f"Preparando limpieza de los datos para el {MIGRATIONS_ANALYSIS}"
    logging(message=message, level="INFO")

    # Limpiamos datos de gpon
    cleaned_df_gpon = __prepare_df_gpon(df_gpon=df_gpon.copy())

    # Limpiamos datos de brownfield
    cleaned_df_brownfield = __prepare_df_brownfield(df_brownfield=df_brownfield.copy())

    # Unimos ambos dataframes
    cleaned_df_brownfield = reorder_columns(
        df=cleaned_df_brownfield,
        order=COLUMN_ORDER,
    )
    cleaned_df_gpon = reorder_columns(df=cleaned_df_gpon, order=COLUMN_ORDER)
    df_output = pd.concat(
        objs=[cleaned_df_gpon, cleaned_df_brownfield],
        ignore_index=True,
    )

    # Creamos archivo de salida
    message = f"Creando archivo: {parameters.MIGRATIONS_ANALYSIS_FILE_PATH}"
    logging(message=message, level="INFO")

    create_file(df=df_output, path=parameters.MIGRATIONS_ANALYSIS_FILE_PATH)

    logging(message="Limpieza completada", level="INFO")

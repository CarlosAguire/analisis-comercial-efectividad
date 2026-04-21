import gc

import pandas as pd

from config import parameters
from data.clean.migrations_analysis import (
    clean_df_brownfield,
    clean_df_gpon,
)
from data.operations import correct_dates, create_file, reorder_columns
from logs_setup import logging

MIGRATIONS_ANALYSIS = parameters.MIGRATIONS_ANALYSIS
COLUMNS_TO_RESERVE = parameters.COLUMNS_TO_RESERVE[MIGRATIONS_ANALYSIS]
COLUMN_ORDER = parameters.COLUMN_ORDER[MIGRATIONS_ANALYSIS]


def __clean_data(df_gpon: pd.DataFrame, df_brownfield: pd.DataFrame) -> pd.DataFrame:
    # Limpiamos datos de gpon
    df_gpon_copy = df_gpon.copy()
    df_gpon_copy = clean_df_gpon(df=df_gpon_copy)

    # Creamos columnas faltantes
    df_gpon_copy = df_gpon_copy.assign(
        **{
            "Tipificación": pd.Series(
                data=pd.NA,
                index=df_gpon_copy.index,
                dtype="string[pyarrow]",
            ),
            "Tipo de Red": pd.Series(
                data="GPON",
                index=df_gpon_copy.index,
                dtype="string[pyarrow]",
            ),
            "Desmonte de Nodos": pd.Series(
                data="NO APLICA",
                index=df_gpon_copy.index,
                dtype="string[pyarrow]",
            ),
            "Nota": pd.Series(
                data="NO REQUIERE",
                index=df_gpon_copy.index,
                dtype="string[pyarrow]",
            ),
        },
    )

    # Reordenamos columnas
    df_gpon_copy = reorder_columns(df=df_gpon_copy, order=COLUMN_ORDER)

    # Limpiamos datos de brownfield
    df_brownfield_copy = df_brownfield.copy()
    df_brownfield_copy = clean_df_brownfield(df=df_brownfield_copy)

    # Creamos columnas faltantes
    df_brownfield_copy = df_brownfield_copy.assign(
        **{
            "Tipo de Red": pd.Series(
                data="HFC",
                index=df_gpon_copy.index,
                dtype="string[pyarrow]",
            ),
            "Código": pd.Series(
                data="NO REQUIERE",
                index=df_brownfield_copy.index,
                dtype="string[pyarrow]",
            ),
        },
    )

    # Reordenamos columnas
    df_brownfield_copy = reorder_columns(df=df_brownfield_copy, order=COLUMN_ORDER)

    # Unimos ambos dataframes
    df_output = pd.concat(
        objs=[df_gpon_copy, df_brownfield_copy],
        ignore_index=True,
    )

    # Eliminamos dataframes que ya no se usaran más para liberar memoria
    del df_gpon_copy
    del df_brownfield_copy
    gc.collect()

    # Corregimos formato de fechas
    df_output = correct_dates(df=df_output, column="Fecha")

    return df_output


def run(df_gpon: pd.DataFrame, df_brownfield: pd.DataFrame) -> None:
    # Iniciamos proceso de limpieza
    message = f"Preparando limpieza de los datos para el {MIGRATIONS_ANALYSIS}"
    logging(message=message, level="INFO")

    df_output = __clean_data(df_gpon=df_gpon, df_brownfield=df_brownfield)

    # Creamos archivo de salida
    logging(
        message=f"Creando archivo: {parameters.MIGRATIONS_ANALYSIS_FILE_PATH}",
        level="INFO",
    )

    create_file(
        df=df_output,
        path=parameters.MIGRATIONS_ANALYSIS_FILE_PATH,
        datetime_format="yyyy-mm-dd hh:mm:ss",
    )

    logging(message="Limpieza completada", level="INFO")

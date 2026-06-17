import pandas as pd

from config import parameters
from logs_setup import logging
from operations.data_frame import create_file, drop_columns, filter_df, reorder_columns

PRODUCTIVITY_ANALYSIS = parameters.PRODUCTIVITY_ANALYSIS
COLUMNS_TO_RESERVE = parameters.COLUMNS_TO_RESERVE[PRODUCTIVITY_ANALYSIS]
FILTERS = parameters.FILTERS[PRODUCTIVITY_ANALYSIS]
COLUMN_ORDER = parameters.COLUMN_ORDER[PRODUCTIVITY_ANALYSIS]


def __prepare_df_ftth_hfc(df_ftth_hfc: pd.DataFrame) -> pd.DataFrame:

    # Filtramos para eliminar filas que no necesitamos
    cleaned_df_ftth_hfc = filter_df(
        filters=FILTERS["capacity_file"],
        df=df_ftth_hfc,
    )

    # Removemos columnas que no necesitamos
    cleaned_df_ftth_hfc = drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["capacity_file"],
        df=cleaned_df_ftth_hfc,
    )

    return cleaned_df_ftth_hfc


def __prepare_df_fo(df_fo: pd.DataFrame) -> pd.DataFrame:

    # Filtramos para eliminar filas que no necesitamos
    cleaned_df_fo = filter_df(
        filters=FILTERS["fo_file"],
        df=df_fo,
    )

    # Removemos columnas que no necesitamos
    cleaned_df_fo = drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["fo_file"],
        df=cleaned_df_fo,
    )

    return cleaned_df_fo


def run(dfs_ftth_hfc: list[pd.DataFrame], dfs_fo: list[pd.DataFrame]) -> None:

    # Iniciamos proceso de limpieza
    message = f"Preparando limpieza de los datos para el {PRODUCTIVITY_ANALYSIS}"
    logging(message=message, level="INFO")

    cleaned_dfs_ftth_hfc: list[pd.DataFrame] = []
    cleaned_dfs_fo: list[pd.DataFrame] = []

    for df_ftth_hfc in dfs_ftth_hfc:
        cleaned_df_ftth_hfc = __prepare_df_ftth_hfc(df_ftth_hfc=df_ftth_hfc.copy())
        cleaned_dfs_ftth_hfc.append(cleaned_df_ftth_hfc)

    for df_fo in dfs_fo:
        cleaned_df_fo = __prepare_df_fo(df_fo=df_fo.copy())
        cleaned_dfs_fo.append(cleaned_df_fo)

    # Unimos todos los dfs del arbol de ftth_hfc y fo
    df_output = pd.concat(
        objs=cleaned_dfs_ftth_hfc + cleaned_dfs_fo,
        ignore_index=True,
    )

    # Reordenamos las columnas
    df_output = reorder_columns(df=df_output, order=COLUMN_ORDER)

    message = f"Creando archivo final: {parameters.PRODUCTIVITY_ANALYSIS_FILE_PATH}"
    logging(message=message, level="INFO")

    create_file(df=df_output, path=parameters.PRODUCTIVITY_ANALYSIS_FILE_PATH)

    logging(message="Limpieza completada", level="INFO")

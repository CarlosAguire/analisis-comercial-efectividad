import pandas as pd

from config import parameters
from logs_setup import logging
from operations.data_frame import create_file

PRODUCTIVITY_ANALYSIS = parameters.PRODUCTIVITY_ANALYSIS


def __prepare_df_ftth_hfc(df_ftth_hfc: pd.DataFrame) -> pd.DataFrame:

    return df_ftth_hfc.copy()


def __prepare_df_fo(df_fo: pd.DataFrame) -> pd.DataFrame:

    return df_fo.copy()


def run(dfs_ftth_hfc: list[pd.DataFrame], dfs_fo: list[pd.DataFrame]) -> None:

    # Iniciamos proceso de limpieza
    message = f"Preparando limpieza de los datos para el {PRODUCTIVITY_ANALYSIS}"
    logging(message=message, level="INFO")

    cleaned_dfs_ftth_hfc: list[pd.DataFrame] = []
    cleaned_dfs_fo: list[pd.DataFrame] = []

    for df_ftth_hfc in dfs_ftth_hfc:
        cleaned_df_ftth_hfc = __prepare_df_ftth_hfc(df_ftth_hfc=df_ftth_hfc)
        cleaned_dfs_ftth_hfc.append(cleaned_df_ftth_hfc)

    for df_fo in dfs_fo:
        cleaned_df_fo = __prepare_df_fo(df_fo=df_fo)
        cleaned_dfs_fo.append(cleaned_df_fo)

    # Unimos todos los dfs del arbol de ftth_hfc y fo
    df_output = pd.concat(
        objs=cleaned_dfs_ftth_hfc + cleaned_dfs_fo,
        ignore_index=True,
    )

    message = f"Creando archivo final: {parameters.PRODUCTIVITY_ANALYSIS_FILE_PATH}"
    logging(message=message, level="INFO")

    create_file(df=df_output, path=parameters.PRODUCTIVITY_ANALYSIS_FILE_PATH)

    logging(message="Limpieza completada", level="INFO")

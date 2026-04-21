import gc

import pandas as pd

from config import parameters
from data.clean.backlog_analysis import (
    clean_df_backlog,
)
from data.operations import create_file
from logs_setup import logging

BACKLOG_ANALYSIS = parameters.BACKLOG_ANALYSIS


def __clean_data(
    df_residential_plant: pd.DataFrame,
    df_backlog: pd.DataFrame,
) -> pd.DataFrame:
    logging(
        message=f"Iniciando limpieza: {df_backlog.attrs['path']}",
        level="INFO",
    )

    df_residential_plant_copy = df_residential_plant.copy()
    df_backlog_copy = df_backlog.copy()

    # Iniciamos a limpiar backlog
    cleaned_df_backlog = clean_df_backlog(
        df_backlog=df_backlog_copy,
        df_residential_plant=df_residential_plant_copy,
    )

    # Eliminamos dataframes que ya no se usaran más para liberar memoria
    del df_residential_plant_copy
    del df_backlog_copy
    gc.collect()

    return cleaned_df_backlog


def run(
    df_residential_plant: pd.DataFrame,
    df_backlog: pd.DataFrame,
) -> None:
    message = f"Preparando limpieza de los datos para el {BACKLOG_ANALYSIS}"
    logging(message=message, level="INFO")

    df_output = __clean_data(
        df_residential_plant=df_residential_plant,
        df_backlog=df_backlog,
    )

    logging(message="Limpieza completada", level="INFO")
    logging(
        message=f"Creando archivo final: {parameters.BACKLOG_ANALYSIS_FILE_PATH}",
        level="INFO",
    )

    create_file(df=df_output, path=parameters.BACKLOG_ANALYSIS_FILE_PATH)

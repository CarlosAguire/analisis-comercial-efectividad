import pandas as pd

from config import parameters
from data.clean.backlog_analysis import (
    clean_df_backlog,
    clean_df_residential_plant,
)
from data.operations import join_by_sales_advisor
from logs_setup import logging

BACKLOG_ANALYSIS = parameters.BACKLOG_ANALYSIS
COLUMNS_TO_RESERVE = parameters.COLUMNS_TO_RESERVE[BACKLOG_ANALYSIS]


def clean_data(
    df_residential_plant: pd.DataFrame,
    df_backlog: pd.DataFrame,
) -> pd.DataFrame:
    logging(
        message=f"Iniciando limpieza: {df_backlog.attrs['path']}",
        level="INFO",
    )

    df_backlog_copy = df_backlog.copy()
    cleaned_df_backlog = clean_df_backlog(df=df_backlog_copy)

    # Iniciamos a limpiar planta residencial
    df_residential_plant_copy = df_residential_plant.copy()
    cleaned_df_residential_plant = clean_df_residential_plant(
        df=df_residential_plant_copy,
        df_backlog=cleaned_df_backlog,
    )

    df_output = join_by_sales_advisor(
        df_dictionary=cleaned_df_residential_plant,
        df=cleaned_df_backlog,
    )
    df_output.rename(
        columns=parameters.FINAL_COLUMNS[BACKLOG_ANALYSIS],
        inplace=True,
    )

    return df_output

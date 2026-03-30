import pandas as pd

from config import parameters
from logs_setup import logging

PRODUCTIVITY_ANALYSIS = parameters.PRODUCTIVITY_ANALYSIS
COLUMNS_TO_RESERVE = parameters.COLUMNS_TO_RESERVE[PRODUCTIVITY_ANALYSIS]


def clean_data(dfs_ofsc_capacity: list[pd.DataFrame]) -> pd.DataFrame:
    cleaned_dfs_ofsc_capacity: list[pd.DataFrame] = []

    for df_ofsc_capacity in dfs_ofsc_capacity:
        logging(
            message=f"Iniciando limpieza: {df_ofsc_capacity.attrs['path']}",
            level="INFO",
        )

        df_ofsc_capacity_copy = df_ofsc_capacity.copy()
        # df_ofsc_capacity_copy = clean_df_ofsc_capacity(df=df_ofsc_capacity_copy)

        cleaned_dfs_ofsc_capacity.append(df_ofsc_capacity_copy)

    cleaned_df_ofsc_capacity = pd.concat(
        objs=cleaned_dfs_ofsc_capacity,
        ignore_index=True,
    )

    return cleaned_df_ofsc_capacity

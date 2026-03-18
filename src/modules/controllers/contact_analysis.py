from copy import deepcopy
from pathlib import Path

import pandas as pd

from config import parameters
from logs_setup import logging
from modules.data.clean.efficacy_analysis import (
    clean_df_ofsc_capacity,
)
from modules.data.operations import (
    read_excel,
)

COMERCIAL_EFFICACY_ANALYSIS = parameters.COMERCIAL_EFFICACY_ANALYSIS
COLUMNS_TO_RESERVE = parameters.COLUMNS_TO_RESERVE[COMERCIAL_EFFICACY_ANALYSIS]


def clean_data(
    df_residential_plant: pd.DataFrame,
    files_path: list[Path],
) -> None:
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

        df_ofsc_capacity = read_excel(path=file_path, sheet=0)
        df_ofsc_capacity = clean_df_ofsc_capacity(df=df_ofsc_capacity)

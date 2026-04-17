import pandas as pd

from config import parameters
from data.clean.manager import CleanDataFrame

MIGRATIONS_ANALYSIS = parameters.MIGRATIONS_ANALYSIS
COLUMNS_TO_RESERVE = parameters.COLUMNS_TO_RESERVE[MIGRATIONS_ANALYSIS]
FINAL_COLUMNS = parameters.FINAL_COLUMNS[MIGRATIONS_ANALYSIS]


def clean_df_gpon(df: pd.DataFrame) -> pd.DataFrame:
    # Removemos columnas que no necesitamos
    df_gpon = CleanDataFrame.drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["gpon_bases"],
        df=df,
    )

    # Renombramos columnas de planta residencial
    df_gpon.rename(
        columns=FINAL_COLUMNS["gpon_bases"],
        inplace=True,
    )

    return df_gpon


def clean_df_brownfield(df: pd.DataFrame) -> pd.DataFrame:
    # Removemos columnas que no necesitamos
    df_brownfield = CleanDataFrame.drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["brownfield_bases"],
        df=df,
    )

    # Renombramos columnas de planta residencial
    df_brownfield.rename(
        columns=FINAL_COLUMNS["brownfield_bases"],
        inplace=True,
    )

    return df_brownfield

import pandas as pd

from config import parameters
from data.clean.manager import CleanDataFrame

BACKLOG_ANALYSIS = parameters.BACKLOG_ANALYSIS
COLUMNS_TO_RESERVE = parameters.COLUMNS_TO_RESERVE[BACKLOG_ANALYSIS]


def clean_df_backlog(df: pd.DataFrame) -> pd.DataFrame:

    # Removemos columnas que no necesitamos
    df_backlog = CleanDataFrame.drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["backlog"],
        df=df,
    )

    # Renombramos columnas
    df_backlog.rename(
        columns={"NOMBRE": "Asesor comercial"},
        inplace=True,
    )

    return df_backlog


def clean_df_residential_plant(
    df: pd.DataFrame,
    df_backlog: pd.DataFrame,
) -> pd.DataFrame:

    # Filtramos para eliminar filas que no necesitamos
    df_residential_plant = CleanDataFrame.filter(
        filters={
            "include": {"NOMBRE": df_backlog["Asesor comercial"].tolist()},
        },
        df=df,
    )

    # Removemos columnas que no necesitamos
    df_residential_plant = CleanDataFrame.drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["residential_plant"],
        df=df_residential_plant,
    )

    # Removemos filas duplicadas que no necesitamos
    df_residential_plant = CleanDataFrame.drop_duplicate_rows_by_column(
        df=df_residential_plant,
        column="NOMBRE",
    )

    # Renombramos columnas
    df_residential_plant.rename(
        columns={"NOMBRE": "Asesor comercial"},
        inplace=True,
    )

    return df_residential_plant

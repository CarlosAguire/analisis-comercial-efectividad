import pandas as pd

from config import parameters
from modules.data.clean.utils import CleanDataFrame

CONTACT_ANALYSIS = parameters.CONTACT_ANALYSIS
FILTERS = parameters.FILTERS[CONTACT_ANALYSIS]
COLUMNS_TO_RESERVE = parameters.COLUMNS_TO_RESERVE[CONTACT_ANALYSIS]


def clean_df_ofsc_capacity(df: pd.DataFrame) -> pd.DataFrame:
    # Filtramos para eliminar filas que no necesitamos
    df_ofsc_dispatch = CleanDataFrame.filter(
        filters=FILTERS["ofsc_capacity"],
        df=df,
    )

    # Removemos columnas que no necesitamos
    df_ofsc_dispatch = CleanDataFrame.drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["ofsc_capacity"],
        df=df_ofsc_dispatch,
    )

    return df_ofsc_dispatch


def clean_df_residential_plant(
    df: pd.DataFrame,
    df_ofsc_capacity: pd.DataFrame,
) -> pd.DataFrame:

    # Filtramos para eliminar filas que no necesitamos
    df_residential_plant = CleanDataFrame.filter(
        filters={"NOMBRE": df_ofsc_capacity["Asesor comercial"].tolist()},
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

    return df_residential_plant

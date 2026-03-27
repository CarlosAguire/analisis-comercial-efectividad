import pandas as pd

from config import parameters
from data.clean.manager import CleanDataFrame

COMERCIAL_EFFICACY_ANALYSIS = parameters.COMERCIAL_EFFICACY_ANALYSIS
FILTERS = parameters.FILTERS[COMERCIAL_EFFICACY_ANALYSIS]
COLUMNS_TO_RESERVE = parameters.COLUMNS_TO_RESERVE[COMERCIAL_EFFICACY_ANALYSIS]


def clean_df_ofsc_dispatch(df: pd.DataFrame) -> pd.DataFrame:
    # Removemos columnas duplicadas que no necesitamos
    df_ofsc_dispatch = CleanDataFrame.drop_duplicate_columns(
        target_column="Notas de Cierre",
        df=df,
    )

    # Filtramos para eliminar filas que no necesitamos
    df_ofsc_dispatch = CleanDataFrame.filter(
        filters=FILTERS["ofsc_dispatch"],
        df=df_ofsc_dispatch,
    )

    # Removemos columnas que no necesitamos
    df_ofsc_dispatch = CleanDataFrame.drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["ofsc_dispatch"],
        df=df_ofsc_dispatch,
    )

    return df_ofsc_dispatch


def clean_df_ofsc_capacity(df: pd.DataFrame) -> pd.DataFrame:
    # Filtramos para eliminar filas que no necesitamos
    df_ofsc_capacity = CleanDataFrame.filter(
        filters=FILTERS["ofsc_capacity"],
        df=df,
    )

    # 3. Removemos columnas que no necesitamos
    df_ofsc_capacity = CleanDataFrame.drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["ofsc_capacity"],
        df=df_ofsc_capacity,
    )

    return df_ofsc_capacity


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

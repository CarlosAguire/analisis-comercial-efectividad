import gc

import pandas as pd

from config import parameters
from data.clean.manager import CleanDataFrame
from data.operations import complete_data

BACKLOG_ANALYSIS = parameters.BACKLOG_ANALYSIS
COLUMNS_TO_RESERVE = parameters.COLUMNS_TO_RESERVE[BACKLOG_ANALYSIS]
FILTERS = parameters.FILTERS[BACKLOG_ANALYSIS]
FINAL_COLUMNS = parameters.FINAL_COLUMNS[BACKLOG_ANALYSIS]


def clean_df_backlog(
    df_backlog: pd.DataFrame,
    df_residential_plant: pd.DataFrame,
) -> pd.DataFrame:
    # Ajustamos tipos de datos
    # fmt: off
    df_backlog_copy = df_backlog.copy()
    df_backlog_copy["CEDULA_VENDEDOR"] = (
        df_backlog_copy["CEDULA_VENDEDOR"].astype("Int64").astype("string")
    )

    df_residential_plant_copy = df_residential_plant.copy()
    df_residential_plant_copy["CC_COMPLETA"] = (
        df_residential_plant_copy["CC_COMPLETA"].astype(dtype="string")
    )
    # fmt: on

    # Removemos columnas que no necesitamos
    df_backlog_copy = CleanDataFrame.drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["backlog"],
        df=df_backlog_copy,
    )
    df_residential_plant_copy = CleanDataFrame.drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["residential_plant"],
        df=df_residential_plant_copy,
    )

    # Filtramos para eliminar filas que no necesitamos
    df_backlog_copy = CleanDataFrame.filter(
        filters=FILTERS["backlog"],
        df=df_backlog_copy,
    )
    sellers = df_backlog_copy["CEDULA_VENDEDOR"].unique().tolist()
    df_residential_plant_copy = CleanDataFrame.filter(
        df=df_residential_plant_copy,
        filters={"contains": {"CC_COMPLETA": sellers, "TCARGU": sellers}},
        combine="or",
    )

    # Completamos las columnas del backlog con la información de planta residencial
    df_residential_plant_copy = df_residential_plant_copy.rename(
        columns={"CC_COMPLETA": "CEDULA_VENDEDOR"},
    )
    df_backlog_copy["GV-Especialista"] = None
    df_backlog_copy["GV-Descripcion"] = None
    df_backlog_copy["JEFE 1 CANAL REGIONAL"] = None
    df_backlog_copy["CANAL2"] = None
    df_output = complete_data(
        df=df_backlog_copy,
        df_dictionary=df_residential_plant_copy,
        column="CEDULA_VENDEDOR",
        key_match="contains",
    )
    df_residential_plant_copy = df_residential_plant_copy.drop(
        columns=["CEDULA_VENDEDOR"]
    )
    df_residential_plant_copy = df_residential_plant_copy.rename(
        columns={"TCARGU": "CEDULA_VENDEDOR"},
    )
    df_output = complete_data(
        df=df_backlog_copy,
        df_dictionary=df_residential_plant_copy,
        column="CEDULA_VENDEDOR",
        key_match="contains",
    )

    # Eliminamos dataframes que ya no se usaran más para liberar memoria
    del df_residential_plant_copy
    del df_backlog_copy
    gc.collect()

    # Renombramos columnas
    # df_output.rename(columns=FINAL_COLUMNS, inplace=True)

    return df_output

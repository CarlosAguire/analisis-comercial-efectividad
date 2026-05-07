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

    # Normalizamos los nombres de las columnas
    df_backlog.columns = df_backlog.columns.str.replace(
        pat="ï»¿",
        repl="",
        regex=False,
    ).str.strip()

    # Ajustamos tipos de datos
    # fmt: off
    df_backlog["HORA_CREADO"] = df_backlog["HORA_CREADO"].astype("string")
    df_backlog["Hora_AMPM"] = (
        pd.to_datetime(
            df_backlog["HORA_CREADO"].astype("string").str.zfill(6),
            format="%H%M%S",
            errors="coerce",
        )
        .dt.strftime("%I:%M %p")
    )
    df_backlog = df_backlog.drop(columns=["HORA_CREADO"])
    df_backlog = df_backlog.rename(columns={"Hora_AMPM": "HORA_CREADO"})
    df_backlog["CEDULA_VENDEDOR"] = (
        df_backlog["CEDULA_VENDEDOR"]
        .astype("string")
        .str.replace(r"\.0$", "", regex=True)
    )
    df_residential_plant["CC_COMPLETA"] = (
        df_residential_plant["CC_COMPLETA"]
        .astype(dtype="string")
        .str.replace(r"\.0$", "", regex=True)
    )
    # fmt: on

    # Removemos columnas que no necesitamos
    df_backlog = CleanDataFrame.drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["backlog"],
        df=df_backlog,
    )
    df_residential_plant = CleanDataFrame.drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["residential_plant"],
        df=df_residential_plant,
    )

    # Filtramos para eliminar filas que no necesitamos
    df_backlog = CleanDataFrame.filter(
        filters=FILTERS["backlog"],
        df=df_backlog,
    )
    sellers = df_backlog["CEDULA_VENDEDOR"].unique().tolist()
    df_residential_plant = CleanDataFrame.filter(
        df=df_residential_plant,
        filters={"contains": {"CC_COMPLETA": sellers, "TCARGU": sellers}},
        combine="or",
    )

    # Completamos las columnas del backlog con la información de planta residencial
    df_residential_plant = df_residential_plant.rename(
        columns={"CC_COMPLETA": "CEDULA_VENDEDOR"},
    )
    df_backlog["GV-Especialista"] = None
    df_backlog["GV-Descripcion"] = None
    df_backlog["JEFE 1 CANAL REGIONAL"] = None
    df_backlog["CANAL2"] = None
    df_output = complete_data(
        df=df_backlog,
        df_dictionary=df_residential_plant,
        column="CEDULA_VENDEDOR",
        key_match="contains",
    )
    df_residential_plant = df_residential_plant.drop(columns=["CEDULA_VENDEDOR"])
    df_residential_plant = df_residential_plant.rename(
        columns={"TCARGU": "CEDULA_VENDEDOR"},
    )

    df_output = complete_data(
        df=df_output,
        df_dictionary=df_residential_plant,
        column="CEDULA_VENDEDOR",
        key_match="contains",
    )

    # Renombramos columnas
    df_output.rename(columns=FINAL_COLUMNS, inplace=True)

    return df_output

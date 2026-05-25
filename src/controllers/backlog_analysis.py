import pandas as pd

from config import parameters
from logs_setup import logging
from operations.data_frame import complete_data, create_file, drop_columns, filter_df

BACKLOG_ANALYSIS = parameters.BACKLOG_ANALYSIS
FINAL_COLUMNS = parameters.FINAL_COLUMNS[BACKLOG_ANALYSIS]
COLUMNS_TO_RESERVE = parameters.COLUMNS_TO_RESERVE[BACKLOG_ANALYSIS]
FILTERS = parameters.FILTERS[BACKLOG_ANALYSIS]


def __prepare_df_backlog(
    df_backlog: pd.DataFrame,
    df_residential_plant: pd.DataFrame,
    df_ftth_hfc: pd.DataFrame,
    df_fo: pd.DataFrame,
) -> pd.DataFrame:
    message = f"Iniciando limpieza: {df_backlog.attrs['file_path']}"
    logging(message=message, level="INFO")

    # Normalizamos los nombres de las columnas de df_backlog
    df_backlog.columns = df_backlog.columns.str.replace(
        pat="ï»¿",
        repl="",
        regex=False,
    ).str.strip()

    # Ajustamos tipos de datos de df_backlog
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

    # Filtramos para eliminar filas que no necesitamos de df_backlog
    cleaned_df_backlog = filter_df(
        filters=FILTERS["backlog_file"],
        df=df_backlog,
    )
    sellers = cleaned_df_backlog["CEDULA_VENDEDOR"].unique().tolist()
    cleaned_df_residential_plant = filter_df(
        df=df_residential_plant,
        filters={"contains": {"CC_COMPLETA": sellers, "TCARGU": sellers}},
        combine="or",
    )

    # Removemos columnas que no necesitamos de df_backlog
    cleaned_df_backlog = drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["backlog_file"],
        df=cleaned_df_backlog,
    )
    cleaned_df_residential_plant = drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["residential_plant_file"],
        df=cleaned_df_residential_plant,
    )

    # Completamos las columnas de df_backlog con la información de df_residential_plant
    cleaned_df_residential_plant = cleaned_df_residential_plant.rename(
        columns={"CC_COMPLETA": "CEDULA_VENDEDOR"},
    )
    cleaned_df_backlog["GV-Especialista"] = None
    cleaned_df_backlog["GV-Descripcion"] = None
    cleaned_df_backlog["JEFE 1 CANAL REGIONAL"] = None
    cleaned_df_backlog["CANAL2"] = None
    cleaned_df_backlog = complete_data(
        df=cleaned_df_backlog,
        df_dictionary=cleaned_df_residential_plant,
        column="CEDULA_VENDEDOR",
        key_match="contains",
    )
    cleaned_df_residential_plant = cleaned_df_residential_plant.drop(
        columns=["CEDULA_VENDEDOR"]
    )
    cleaned_df_residential_plant = cleaned_df_residential_plant.rename(
        columns={"TCARGU": "CEDULA_VENDEDOR"},
    )
    cleaned_df_backlog = complete_data(
        df=cleaned_df_backlog,
        df_dictionary=cleaned_df_residential_plant,
        column="CEDULA_VENDEDOR",
        key_match="contains",
    )

    # Unimos de manera verical df_ftth_hfc y df_fo
    cleaned_df_ofsc = pd.concat(
        objs=[df_ftth_hfc, df_fo],
        ignore_index=True,
    )

    # Completamos las columnas de df_backlog con la información de cleaned_df_ofsc
    cleaned_df_backlog["Ventana de servicio"] = None
    cleaned_df_backlog = complete_data(
        df_dictionary=cleaned_df_ofsc,
        df=cleaned_df_backlog,
        column="OT",
        key_match="contains",
    )

    # Renombramos columnas
    cleaned_df_backlog.rename(columns=FINAL_COLUMNS, inplace=True)

    return cleaned_df_backlog


def __prepare_df_ftth_hfc(df_ftth_hfc: pd.DataFrame) -> pd.DataFrame:
    message = f"Iniciando limpieza: {df_ftth_hfc.attrs['file_path']}"
    logging(message=message, level="INFO")

    # Removemos columnas que no necesitamos
    cleaned_df_ftth_hfc = drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["capacity_file"],
        df=df_ftth_hfc,
    )

    # Renombramos columnas
    cleaned_df_ftth_hfc.rename(columns={"Orden de trabajo": "OT"}, inplace=True)

    return cleaned_df_ftth_hfc


def __prepare_df_fo(df_fo: pd.DataFrame) -> pd.DataFrame:
    message = f"Iniciando limpieza: {df_fo.attrs['file_path']}"
    logging(message=message, level="INFO")

    # Removemos columnas que no necesitamos
    cleaned_df_fo = drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["fo_file"],
        df=df_fo,
    )

    # Renombramos columnas
    cleaned_df_fo.rename(columns={"Orden de trabajo": "OT"}, inplace=True)

    return cleaned_df_fo


def run(
    df_residential_plant: pd.DataFrame,
    df_backlog: pd.DataFrame,
    df_ftth_hfc: pd.DataFrame,
    df_fo: pd.DataFrame,
) -> None:
    message = f"Preparando limpieza de los datos para el {BACKLOG_ANALYSIS}"
    logging(message=message, level="INFO")

    cleaned_df_ftth_hfc = __prepare_df_ftth_hfc(df_ftth_hfc=df_ftth_hfc.copy())
    cleaned_df_fo = __prepare_df_fo(df_fo=df_fo.copy())
    df_output = __prepare_df_backlog(
        df_residential_plant=df_residential_plant.copy(),
        df_backlog=df_backlog.copy(),
        df_ftth_hfc=cleaned_df_ftth_hfc,
        df_fo=cleaned_df_fo,
    )

    message = "Limpieza de los datos completada"
    logging(message=message, level="INFO")
    message = f"Creando archivo final: {parameters.BACKLOG_ANALYSIS_FILE_PATH}"
    logging(message=message, level="INFO")

    create_file(df=df_output, path=parameters.BACKLOG_ANALYSIS_FILE_PATH)

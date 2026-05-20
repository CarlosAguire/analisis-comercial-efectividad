import gc

import pandas as pd

from config import parameters
from logs_setup import logging
from operations.clean.backlog_analysis import (
    clean_df_backlog,
    clean_df_ofsc,
    clean_df_ofsc_capacity,
    clean_df_residential_plant,
)
from operations.clean.manager import CleanDataFrame
from operations.data_frame import complete_data, create_file

BACKLOG_ANALYSIS = parameters.BACKLOG_ANALYSIS
FINAL_COLUMNS = parameters.FINAL_COLUMNS[BACKLOG_ANALYSIS]


def __clean_data(
    df_residential_plant: pd.DataFrame,
    dfs_ofsc_capacity: list[pd.DataFrame],
    dfs_ofsc: list[pd.DataFrame],
    df_backlog: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    logging(
        message=f"Iniciando limpieza: {df_backlog.attrs['path']}",
        level="INFO",
    )

    df_residential_plant_copy = df_residential_plant.copy()
    df_backlog_copy = df_backlog.copy()

    # Iniciamos a limpiar backlog
    cleaned_df_backlog = clean_df_backlog(
        df_backlog=df_backlog_copy,
        df_residential_plant=df_residential_plant_copy,
    )

    # Iniciamos limpieza de los archivos de OFSC
    cleaned_dfs_ofsc: list[pd.DataFrame] = []

    for df in dfs_ofsc:
        logging(message=f"Iniciando limpieza: {df.attrs['path']}", level="INFO")

        df_copy = df.copy()
        df_copy = clean_df_ofsc(df=df_copy)
        cleaned_dfs_ofsc.append(df_copy)

    # Unimos todos loas archivos de OFSC
    cleaned_df_ofsc = pd.concat(
        objs=cleaned_dfs_ofsc,
        ignore_index=True,
    )

    # Completamos la data uniendo backlog con OFSC
    logging(message="Completando datos", level="INFO")

    cleaned_df_backlog["Ventana de servicio"] = None
    df_backlog = complete_data(
        df_dictionary=cleaned_df_ofsc,
        df=cleaned_df_backlog,
        column="OT",
        key_match="contains",
    )

    # Iniciamos limpieza de los archivos de capacidad de OFSC
    cleaned_dfs_residential_plant: list[pd.DataFrame] = []
    cleaned_dfs_capacity: list[pd.DataFrame] = []

    for df in dfs_ofsc_capacity:
        logging(
            message=f"Iniciando limpieza: {df.attrs['path']}",
            level="INFO",
        )

        df_ofsc_capacity_copy = df.copy()
        df_ofsc_capacity_copy = clean_df_ofsc_capacity(df=df_ofsc_capacity_copy)

        df_residential_plant_copy = df_residential_plant.copy()
        df_residential_plant_copy = clean_df_residential_plant(
            df_ofsc_capacity=df_ofsc_capacity_copy,
            df_residential_plant=df_residential_plant_copy,
        )

        cleaned_dfs_residential_plant.append(df_residential_plant_copy)
        cleaned_dfs_capacity.append(df_ofsc_capacity_copy)

    df_backlog_onnet = pd.concat(
        objs=cleaned_dfs_capacity,
        ignore_index=True,
    )
    df_residential_plant = pd.concat(
        objs=cleaned_dfs_residential_plant,
        ignore_index=True,
    )
    df_residential_plant = CleanDataFrame.drop_duplicate_rows_by_column(
        df=df_residential_plant,
        column="Asesor comercial",
    )
    df_backlog_onnet["GV-Especialista"] = None
    df_backlog_onnet["GV-Descripcion"] = None
    df_backlog_onnet["JEFE 1 CANAL REGIONAL"] = None
    df_backlog_onnet["CANAL2"] = None
    df_backlog_onnet = complete_data(
        df_dictionary=df_residential_plant,
        df=df_backlog_onnet,
        column="Asesor comercial",
        key_match="contains",
    )

    # Renombramos columnas
    df_backlog_onnet.rename(columns=FINAL_COLUMNS["backlog_onnet"], inplace=True)

    # Completamos la data uniendo backlog con OFSC
    logging(message="Completando datos", level="INFO")

    cleaned_df_backlog["Ventana de servicio"] = None
    df_backlog = complete_data(
        df_dictionary=cleaned_df_ofsc,
        df=cleaned_df_backlog,
        column="OT",
        key_match="contains",
    )

    # Eliminamos dataframes que ya no se usaran más para liberar memoria
    for df in cleaned_dfs_ofsc + cleaned_dfs_residential_plant + cleaned_dfs_capacity:
        del df

    del df_residential_plant_copy
    del df_backlog_copy
    del cleaned_df_backlog
    del cleaned_df_ofsc

    gc.collect()

    return df_backlog, df_backlog_onnet


def run(
    df_residential_plant: pd.DataFrame,
    df_backlog: pd.DataFrame,
    dfs_ofsc: list[pd.DataFrame],
    dfs_ofsc_capacity: list[pd.DataFrame],
) -> None:
    message = f"Preparando limpieza de los datos para el {BACKLOG_ANALYSIS}"
    logging(message=message, level="INFO")

    df_backlog, df_backlog_onnet = __clean_data(
        df_residential_plant=df_residential_plant,
        df_backlog=df_backlog,
        dfs_ofsc_capacity=dfs_ofsc_capacity,
        dfs_ofsc=dfs_ofsc,
    )

    logging(message="Limpieza completada", level="INFO")
    logging(
        message=f"Creando archivo final: {parameters.BACKLOG_ANALYSIS_FILE_PATH}",
        level="INFO",
    )
    logging(
        message=f"Creando archivo final: {parameters.BACKLOG_ONNET_ANALYSIS_FILE_PATH}",
        level="INFO",
    )

    create_file(df=df_backlog, path=parameters.BACKLOG_ANALYSIS_FILE_PATH)
    create_file(df=df_backlog_onnet, path=parameters.BACKLOG_ONNET_ANALYSIS_FILE_PATH)

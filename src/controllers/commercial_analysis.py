import gc

import pandas as pd

from config import parameters
from data.clean.commercial_analysis import (
    clean_df_ofsc_capacity,
    clean_df_ofsc_dispatch,
    clean_df_residential_plant,
)
from data.clean.manager import CleanDataFrame
from data.operations import (
    complete_data,
    create_file,
    join,
    normalize_date,
    reorder_columns,
)
from logs_setup import logging

COMERCIAL_EFFICACY_ANALYSIS = parameters.COMERCIAL_EFFICACY_ANALYSIS
COLUMNS_TO_RESERVE = parameters.COLUMNS_TO_RESERVE[COMERCIAL_EFFICACY_ANALYSIS]
COLUMN_ORDER = parameters.COLUMN_ORDER[COMERCIAL_EFFICACY_ANALYSIS]


def __clean_data(
    df_residential_plant: pd.DataFrame,
    dfs_ofsc_capacity: list[pd.DataFrame],
    dfs_ofsc_dispatch: list[pd.DataFrame],
) -> pd.DataFrame:
    cleaned_dfs_residential_plant: list[pd.DataFrame] = []
    cleaned_dfs_ofsc_capacity: list[pd.DataFrame] = []
    cleaned_dfs_ofsc_dispatch: list[pd.DataFrame] = []

    # Iniciamos limpieza de los archivos del área de capacidades
    for df_ofsc_capacity in dfs_ofsc_capacity:
        logging(
            message=f"Iniciando limpieza: {df_ofsc_capacity.attrs['path']}",
            level="INFO",
        )

        df_ofsc_capacity_copy = df_ofsc_capacity.copy()
        df_ofsc_capacity_copy = clean_df_ofsc_capacity(df=df_ofsc_capacity_copy)

        df_residential_plant_copy = df_residential_plant.copy()
        df_residential_plant_copy = clean_df_residential_plant(
            df_ofsc_capacity=df_ofsc_capacity_copy,
            df=df_residential_plant_copy,
        )

        # Renombramos columnas de planta residencial
        df_residential_plant_copy.rename(
            columns={"NOMBRE": "Asesor comercial"},
            inplace=True,
        )

        cleaned_dfs_ofsc_capacity.append(df_ofsc_capacity_copy)
        cleaned_dfs_residential_plant.append(df_residential_plant_copy)

    # Iniciamos limpieza de los archivos del área de despacho
    for df_ofsc_dispatch in dfs_ofsc_dispatch:
        logging(
            message=f"Iniciando limpieza: {df_ofsc_dispatch.attrs['path']}",
            level="INFO",
        )

        df_ofsc_dispatch_copy = df_ofsc_dispatch.copy()
        df_ofsc_dispatch_copy = clean_df_ofsc_dispatch(df=df_ofsc_dispatch_copy)
        cleaned_dfs_ofsc_dispatch.append(df_ofsc_dispatch_copy)

    # Unimos todos loas archivos del área de capacidades en uno solo
    df_ofsc_capacity = pd.concat(
        objs=cleaned_dfs_ofsc_capacity,
        ignore_index=True,
    )
    df_ofsc_capacity = normalize_date(
        df=df_ofsc_capacity,
        column="Fecha",
        input_format="dd/mm/yy",
    )

    # Unimos todos loas archivos del área de despacho en uno solo
    df_ofsc_dispatch = pd.concat(
        objs=cleaned_dfs_ofsc_dispatch,
        ignore_index=True,
    )
    df_ofsc_dispatch = normalize_date(
        df=df_ofsc_dispatch,
        column="Fecha",
        input_format="mm/dd/yy",
    )

    # Eliminamos dataframes que ya no se usaran más para liberar memoria
    for df in cleaned_dfs_ofsc_capacity + cleaned_dfs_ofsc_dispatch:
        del df

    gc.collect()

    if parameters.DEBUG:
        logging(
            message=f"Creando archivo: {parameters.COMERCIAL_OFSC_CAPACITY_PATH}",
            level="INFO",
        )
        logging(
            message=f"Creando archivo: {parameters.COMERCIAL_OFSC_DISPATCH_PATH}",
            level="INFO",
        )

        create_file(
            df=df_ofsc_capacity,
            path=parameters.COMERCIAL_OFSC_CAPACITY_PATH,
        )
        create_file(
            df=df_ofsc_dispatch,
            path=parameters.COMERCIAL_OFSC_DISPATCH_PATH,
        )

    # Unimos el archovo del área de capacidades y despacho en uno solo
    logging(message="Uniendo todos los OFSC de despacho y capacidades...", level="INFO")

    df_ofsc = join(
        df1=df_ofsc_dispatch,
        df2=df_ofsc_capacity,
        foreign_key="Orden de trabajo",
        date_column="Fecha",
        time_column="Inicio",
        columns_df1=COLUMNS_TO_RESERVE["ofsc_dispatch"],
        columns_df2=COLUMNS_TO_RESERVE["ofsc_capacity"],
    )

    # Eliminamos dataframes que ya no se usaran más para liberar memoria
    del df_ofsc_dispatch
    del df_ofsc_capacity
    gc.collect()

    if parameters.DEBUG:
        logging(
            message=f"Creando archivo: {parameters.COMERCIAL_OFSC_PATH}",
            level="INFO",
        )

        create_file(df=df_ofsc, path=parameters.COMERCIAL_OFSC_PATH)

    # Unimos todos los archivos de planta residencial en uno solo
    logging(message="Uniendo OFSC y Planta Residencial...", level="INFO")

    df_residential_plant = pd.concat(
        objs=cleaned_dfs_residential_plant,
        ignore_index=True,
    )
    df_residential_plant = CleanDataFrame.drop_duplicate_rows_by_column(
        df=df_residential_plant,
        column="Asesor comercial",
    )

    # Eliminamos dataframes que ya no se usaran más para liberar memoria
    for df in cleaned_dfs_residential_plant:
        del df

    gc.collect()

    if parameters.DEBUG:
        logging(
            message=f"Creando archivo: {parameters.COMERCIAL_RESIDENTIAL_PLANT_PATH}",
            level="INFO",
        )

        create_file(
            path=parameters.COMERCIAL_RESIDENTIAL_PLANT_PATH,
            df=df_residential_plant,
        )

    # Unimos el archivo de OFSC con el de planta residencial en uno solo
    logging(message="Uniendo OFSC y Planta Residencial...", level="INFO")

    df_ofsc["GV-Especialista"] = None
    df_ofsc["GV-Descripcion"] = None
    df_ofsc["JEFE 1 CANAL REGIONAL"] = None
    df_ofsc["CANAL2"] = None
    df_output = complete_data(
        df_dictionary=df_residential_plant,
        df=df_ofsc,
        column="Asesor comercial",
        key_match="contains",
    )

    # Eliminamos dataframes que ya no se usaran más para liberar memoria
    del df_residential_plant
    del df_ofsc
    gc.collect()

    # Ultimos ajustes
    df_output["Razón Sugerida"] = None
    df_output["Estado de la Razón"] = None

    df_output["Notas de Cierre"] = (
        df_output["Notas de Cierre"]
        .astype(str)
        .str.translate(str.maketrans("", "", "'\""))
    )

    # Renombramos columnas
    df_output.rename(
        columns=parameters.FINAL_COLUMNS[COMERCIAL_EFFICACY_ANALYSIS],
        inplace=True,
    )

    # Reordenamos columnas
    df_output = reorder_columns(df=df_output, order=COLUMN_ORDER)

    # Reindexamos el dataframe y creamos columna de id
    df_output = df_output.reset_index(drop=True)
    df_output["id"] = df_output.index + 1

    return df_output


def run(
    df_residential_plant: pd.DataFrame,
    dfs_ofsc_capacity: list[pd.DataFrame],
    dfs_ofsc_dispatch: list[pd.DataFrame],
) -> None:
    # Iniciamos proceso de limpieza
    message = f"Preparando limpieza de los datos para el {COMERCIAL_EFFICACY_ANALYSIS}"
    logging(message=message, level="INFO")

    df_output = __clean_data(
        df_residential_plant=df_residential_plant,
        dfs_ofsc_capacity=dfs_ofsc_capacity,
        dfs_ofsc_dispatch=dfs_ofsc_dispatch,
    )

    # Creamos archivo de salida
    logging(
        message=f"Creando archivo: {parameters.EFFICACY_ANALYSIS_FILE_PATH}",
        level="INFO",
    )

    create_file(df=df_output, path=parameters.EFFICACY_ANALYSIS_FILE_PATH)

    logging(message="Limpieza completada", level="INFO")

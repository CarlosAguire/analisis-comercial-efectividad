from copy import deepcopy

import pandas as pd

from config import parameters
from logs_setup import logging
from modules.data.clean.efficacy_analysis import (
    clean_df_ofsc_capacity,
    clean_df_ofsc_dispatch,
    clean_df_residential_plant,
)
from modules.data.clean.utils import CleanDataFrame
from modules.data.match_files import PairingResult
from modules.data.operations import (
    create_file,
    join,
    join_by_sales_advisor,
    normalize_date,
    read_excel,
)

COMERCIAL_EFFICACY_ANALYSIS = parameters.COMERCIAL_EFFICACY_ANALYSIS
COLUMNS_TO_RESERVE = parameters.COLUMNS_TO_RESERVE[COMERCIAL_EFFICACY_ANALYSIS]


def clean_data(
    df_residential_plant: pd.DataFrame,
    files_path: PairingResult,
) -> None:
    NEW_RESIDENTIAL_PLANT_COLUMNS: list[str] = []
    dfs_residential_plant: list[pd.DataFrame] = []
    dfs_ofsc_capacity: list[pd.DataFrame] = []
    dfs_ofsc_dispatch: list[pd.DataFrame] = []

    logging(
        message=f"Iniciando limpieza: {parameters.RESIDENTIAL_PLANT_PATH}",
        level="INFO",
    )

    for path_ofsc_capacity_file, path_ofsc_dispatch_file in files_path.pairs:
        RESIDENTIAL_PLANT_COLUMNS = deepcopy(COLUMNS_TO_RESERVE["residential_plant"])

        logging(message=f"Iniciando limpieza: {path_ofsc_capacity_file}", level="INFO")

        df_ofsc_capacity = read_excel(path=path_ofsc_capacity_file, sheet=0)
        df_ofsc_capacity = clean_df_ofsc_capacity(df=df_ofsc_capacity)

        logging(message=f"Iniciando limpieza: {path_ofsc_dispatch_file}", level="INFO")

        df_ofsc_dispatch = read_excel(path=path_ofsc_dispatch_file, sheet=0)
        df_ofsc_dispatch = clean_df_ofsc_dispatch(df=df_ofsc_dispatch)

        # Iniciamos a limpiar planta residencial
        df_residential_plant_copy = df_residential_plant.copy()
        df_residential_plant_copy = clean_df_residential_plant(
            df=df_residential_plant_copy,
            df_ofsc_capacity=df_ofsc_capacity,
        )

        # Renombramos columnas de planta residencial
        df_residential_plant_copy.rename(
            columns={"NOMBRE": "Asesor comercial"},
            inplace=True,
        )

        index = 0

        for campo in COLUMNS_TO_RESERVE["residential_plant"]:
            if campo == "NOMBRE":
                break

            index = index + 1

        RESIDENTIAL_PLANT_COLUMNS.pop(index)
        RESIDENTIAL_PLANT_COLUMNS.append("Asesor comercial")

        if not NEW_RESIDENTIAL_PLANT_COLUMNS:
            NEW_RESIDENTIAL_PLANT_COLUMNS.extend(RESIDENTIAL_PLANT_COLUMNS)

        dfs_ofsc_capacity.append(df_ofsc_capacity)
        dfs_ofsc_dispatch.append(df_ofsc_dispatch)
        dfs_residential_plant.append(df_residential_plant_copy)

    df_ofsc_capacity = pd.concat(objs=dfs_ofsc_capacity, ignore_index=True)
    df_ofsc_capacity = normalize_date(
        df=df_ofsc_capacity,
        column="Fecha",
        input_format="dd/mm/yy",
    )
    df_ofsc_dispatch = pd.concat(objs=dfs_ofsc_dispatch, ignore_index=True)
    df_ofsc_dispatch = normalize_date(
        df=df_ofsc_dispatch,
        column="Fecha",
        input_format="mm/dd/yy",
    )

    if parameters.DEBUG:
        logging(
            message=f"Creando archivo: {parameters.CLEAN_OFSC_CAPACITY_PATH}",
            level="INFO",
        )
        logging(
            message=f"Creando archivo: {parameters.CLEAN_OFSC_DISPATCH_PATH}",
            level="INFO",
        )

        create_file(df=df_ofsc_capacity, path=parameters.CLEAN_OFSC_CAPACITY_PATH)
        create_file(df=df_ofsc_dispatch, path=parameters.CLEAN_OFSC_DISPATCH_PATH)

    # Unimos el OFSC de despacho y capacidades en uno solo
    logging(message="Uniendo todos los OFSC de despacho y capacidades...", level="INFO")

    df_ofsc = join(
        df1=df_ofsc_dispatch,
        df2=df_ofsc_capacity,
        foreign_key="Orden de trabajo",
        date_column="Fecha",
        columns_df1=COLUMNS_TO_RESERVE["ofsc_dispatch"],
        columns_df2=COLUMNS_TO_RESERVE["ofsc_capacity"],
    )

    if parameters.DEBUG:
        logging(message=f"Creando archivo: {parameters.CLEAN_OFSC_PATH}", level="INFO")

        create_file(df=df_ofsc, path=parameters.CLEAN_OFSC_PATH)

    # Unimos OFSC y Planta residencial en uno solo
    logging(message="Uniendo OFSC y Planta Residencial...", level="INFO")

    df_residential_plant = pd.concat(objs=dfs_residential_plant, ignore_index=True)
    df_residential_plant = CleanDataFrame.drop_duplicate_rows_by_column(
        df=df_residential_plant,
        column="Asesor comercial",
    )

    if parameters.DEBUG:
        logging(
            message=f"Creando archivo: {parameters.CLEAN_RESIDENTIAL_PLANT_PATH}",
            level="INFO",
        )

        create_file(
            path=parameters.CLEAN_RESIDENTIAL_PLANT_PATH,
            df=df_residential_plant,
        )

    df_output = join_by_sales_advisor(
        df=df_ofsc,
        df_dictionary=df_residential_plant,
    )
    df_output["Razón Sugerida"] = None
    df_output["Estado de la Razón"] = None

    df_output.rename(
        columns=parameters.FINAL_COLUMNS[COMERCIAL_EFFICACY_ANALYSIS],
        inplace=True,
    )

    # 9. Creamos la tabla final
    logging(
        message=f"Creando archivo: {parameters.EFFICACY_ANALYSIS_FILE_PATH}...",
        level="INFO",
    )

    create_file(df=df_output, path=parameters.EFFICACY_ANALYSIS_FILE_PATH)

    logging(message="LIMPIEZA COMPLETADA.", level="INFO")

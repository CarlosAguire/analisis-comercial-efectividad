import pandas as pd

from config import parameters
from data.clean.commercial_analysis import (
    clean_df_ofsc_capacity,
    clean_df_ofsc_dispatch,
    clean_df_residential_plant,
)
from data.clean.manager import CleanDataFrame
from data.operations import (
    create_file,
    join,
    join_by_sales_advisor,
    normalize_date,
)
from logs_setup import logging

COMERCIAL_EFFICACY_ANALYSIS = parameters.COMERCIAL_EFFICACY_ANALYSIS
COLUMNS_TO_RESERVE = parameters.COLUMNS_TO_RESERVE[COMERCIAL_EFFICACY_ANALYSIS]


def __clean_data(
    df_residential_plant: pd.DataFrame,
    dfs_ofsc_capacity: list[pd.DataFrame],
    dfs_ofsc_dispatch: list[pd.DataFrame],
) -> None:
    cleaned_dfs_residential_plant: list[pd.DataFrame] = []
    cleaned_dfs_ofsc_capacity: list[pd.DataFrame] = []
    cleaned_dfs_ofsc_dispatch: list[pd.DataFrame] = []

    for df_ofsc_capacity in dfs_ofsc_capacity:
        logging(
            message=f"Iniciando limpieza: {df_ofsc_capacity.attrs['path']}",
            level="INFO",
        )

        df_ofsc_capacity_copy = df_ofsc_capacity.copy()
        df_ofsc_capacity_copy = clean_df_ofsc_capacity(df=df_ofsc_capacity_copy)

        # Iniciamos a limpiar planta residencial
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

    for df_ofsc_dispatch in dfs_ofsc_dispatch:
        logging(
            message=f"Iniciando limpieza: {df_ofsc_dispatch.attrs['path']}",
            level="INFO",
        )

        df_ofsc_dispatch_copy = df_ofsc_dispatch.copy()
        df_ofsc_dispatch_copy = clean_df_ofsc_dispatch(df=df_ofsc_dispatch_copy)

        cleaned_dfs_ofsc_dispatch.append(df_ofsc_dispatch_copy)

    cleaned_df_ofsc_capacity = pd.concat(
        objs=cleaned_dfs_ofsc_capacity,
        ignore_index=True,
    )
    cleaned_df_ofsc_capacity = normalize_date(
        df=cleaned_df_ofsc_capacity,
        column="Fecha",
        input_format="dd/mm/yy",
    )
    cleaned_df_ofsc_dispatch = pd.concat(
        objs=cleaned_dfs_ofsc_dispatch,
        ignore_index=True,
    )
    cleaned_df_ofsc_dispatch = normalize_date(
        df=cleaned_df_ofsc_dispatch,
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

        create_file(
            df=cleaned_df_ofsc_capacity,
            path=parameters.CLEAN_OFSC_CAPACITY_PATH,
        )
        create_file(
            df=cleaned_df_ofsc_dispatch,
            path=parameters.CLEAN_OFSC_DISPATCH_PATH,
        )

    # Unimos el OFSC de despacho y capacidades en uno solo
    logging(message="Uniendo todos los OFSC de despacho y capacidades...", level="INFO")

    cleaned_df_ofsc = join(
        df1=cleaned_df_ofsc_dispatch,
        df2=cleaned_df_ofsc_capacity,
        foreign_key="Orden de trabajo",
        date_column="Fecha",
        time_column="Inicio",
        columns_df1=COLUMNS_TO_RESERVE["ofsc_dispatch"],
        columns_df2=COLUMNS_TO_RESERVE["ofsc_capacity"],
    )

    if parameters.DEBUG:
        logging(message=f"Creando archivo: {parameters.CLEAN_OFSC_PATH}", level="INFO")

        create_file(df=cleaned_df_ofsc, path=parameters.CLEAN_OFSC_PATH)

    # Unimos OFSC y Planta residencial en uno solo
    logging(message="Uniendo OFSC y Planta Residencial...", level="INFO")

    cleaned_df_residential_plant = pd.concat(
        objs=cleaned_dfs_residential_plant,
        ignore_index=True,
    )
    cleaned_df_residential_plant = CleanDataFrame.drop_duplicate_rows_by_column(
        df=cleaned_df_residential_plant,
        column="Asesor comercial",
    )

    if parameters.DEBUG:
        logging(
            message=f"Creando archivo: {parameters.CLEAN_RESIDENTIAL_PLANT_PATH}",
            level="INFO",
        )

        create_file(
            path=parameters.CLEAN_RESIDENTIAL_PLANT_PATH,
            df=cleaned_df_residential_plant,
        )

    df_output = join_by_sales_advisor(
        df_dictionary=cleaned_df_residential_plant,
        df=cleaned_df_ofsc,
    )
    df_output["Razón Sugerida"] = None
    df_output["Estado de la Razón"] = None

    df_output.rename(
        columns=parameters.FINAL_COLUMNS[COMERCIAL_EFFICACY_ANALYSIS],
        inplace=True,
    )

    # 9. Creamos la tabla final
    logging(
        message=f"Creando archivo: {parameters.EFFICACY_ANALYSIS_FILE_PATH}",
        level="INFO",
    )

    create_file(df=df_output, path=parameters.EFFICACY_ANALYSIS_FILE_PATH)


def run(
    df_residential_plant: pd.DataFrame,
    dfs_ofsc_capacity: list[pd.DataFrame],
    dfs_ofsc_dispatch: list[pd.DataFrame],
) -> None:
    message = f"Iniciando limpieza de los datos para el {COMERCIAL_EFFICACY_ANALYSIS}"
    logging(message=message, level="INFO")

    __clean_data(
        df_residential_plant=df_residential_plant,
        dfs_ofsc_capacity=dfs_ofsc_capacity,
        dfs_ofsc_dispatch=dfs_ofsc_dispatch,
    )

    logging(message="Limpieza completada", level="INFO")

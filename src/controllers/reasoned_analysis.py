import pandas as pd

from config import parameters
from logs_setup import logging
from operations.data_frame import (
    complete_data,
    create_file,
    drop_columns,
    drop_duplicate_columns,
    drop_duplicate_rows_by_column,
    filter_df,
    join,
    normalize_date,
    reorder_columns,
)

REASONED_ANALYSIS = parameters.REASONED_ANALYSIS
COLUMN_ORDER = parameters.COLUMN_ORDER[REASONED_ANALYSIS]
FILTERS = parameters.FILTERS[REASONED_ANALYSIS]
FINAL_COLUMNS = parameters.FINAL_COLUMNS[REASONED_ANALYSIS]
COLUMNS_TO_RESERVE = parameters.COLUMNS_TO_RESERVE[REASONED_ANALYSIS]


def __prepare_df_capacity(df_capacity: pd.DataFrame) -> pd.DataFrame:

    message = f"Iniciando limpieza: {df_capacity.attrs['file_path']}"
    logging(message=message, level="INFO")

    # Filtramos para eliminar filas que no necesitamos
    cleaned_df_capacity = filter_df(
        filters=FILTERS["capacity_file"],
        df=df_capacity,
    )

    # Removemos columnas que no necesitamos
    cleaned_df_capacity = drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["capacity_file"],
        df=cleaned_df_capacity,
    )

    # Agregamos una columna con la ruta del archivo para futuras referencias
    cleaned_df_capacity["Ruta del Archivo"] = df_capacity.attrs["file_path"]

    return cleaned_df_capacity


def __prepare_df_dispatch(df_dispatch: pd.DataFrame) -> pd.DataFrame:

    message = f"Iniciando limpieza: {df_dispatch.attrs['file_path']}"
    logging(message=message, level="INFO")

    # Filtramos para eliminar filas que no necesitamos
    cleaned_df_dispatch = filter_df(
        filters=FILTERS["dispatch_file"],
        df=df_dispatch,
    )

    # Removemos columnas que no necesitamos
    cleaned_df_dispatch = drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["dispatch_file"],
        df=cleaned_df_dispatch,
    )

    # Removemos columnas duplicadas de df_dispatch
    cleaned_df_dispatch = drop_duplicate_columns(
        target_column="Notas de Cierre",
        df=cleaned_df_dispatch,
    )

    # Agregamos una columna con la ruta del archivo para futuras referencias
    cleaned_df_dispatch["Ruta del Archivo"] = df_dispatch.attrs["file_path"]

    return cleaned_df_dispatch


def __prepare_df_residential_plant(
    df_residential_plant: pd.DataFrame,
    df_capacity: pd.DataFrame,
) -> pd.DataFrame:

    # Filtramos para eliminar filas que no necesitamos
    sellers = df_capacity["Asesor comercial"].unique().tolist()
    cleaned_df_residential_plant = filter_df(
        filters={"include": {"NOMBRE": sellers}},
        df=df_residential_plant,
    )

    # Removemos columnas que no necesitamos
    cleaned_df_residential_plant = drop_columns(
        columns_preserve=COLUMNS_TO_RESERVE["residential_plant_file"],
        df=cleaned_df_residential_plant,
    )

    # Removemos filas duplicadas que no necesitamos
    # Para quedarnos solamente con los asesores comerciales únicos
    cleaned_df_residential_plant = drop_duplicate_rows_by_column(
        df=cleaned_df_residential_plant,
        column="NOMBRE",
    )

    return cleaned_df_residential_plant


def run(
    df_residential_plant: pd.DataFrame,
    dfs_capacity: list[pd.DataFrame],
    dfs_dispatch: list[pd.DataFrame],
) -> None:

    # Iniciamos proceso de limpieza
    message = f"Preparando limpieza de los datos para el {REASONED_ANALYSIS}"
    logging(message=message, level="INFO")

    cleaned_dfs_capacity: list[pd.DataFrame] = []
    cleaned_dfs_dispatch: list[pd.DataFrame] = []

    for df_capacity in dfs_capacity:
        cleaned_df_capacity = __prepare_df_capacity(df_capacity=df_capacity.copy())

        if cleaned_df_capacity.empty:
            continue

        cleaned_df_residential_plant = __prepare_df_residential_plant(
            df_residential_plant=df_residential_plant.copy(),
            df_capacity=cleaned_df_capacity,
        )

        # Renombramos una columna de cleaned_df_residential_plant
        # Para completar los datos de cleaned_df_capacity
        cleaned_df_residential_plant.rename(
            columns={"NOMBRE": "Asesor comercial"},
            inplace=True,
        )
        cleaned_df_capacity["GV-Especialista"] = None
        cleaned_df_capacity["GV-Descripcion"] = None
        cleaned_df_capacity["JEFE 1 CANAL REGIONAL"] = None
        cleaned_df_capacity["CANAL2"] = None
        cleaned_df_capacity = complete_data(
            df_dictionary=cleaned_df_residential_plant,
            df=cleaned_df_capacity,
            column="Asesor comercial",
            key_match="contains",
        )

        cleaned_dfs_capacity.append(cleaned_df_capacity)

    for df_dispatch in dfs_dispatch:
        cleaned_df_dispatch = __prepare_df_dispatch(df_dispatch=df_dispatch.copy())

        if cleaned_df_dispatch.empty:
            continue

        cleaned_dfs_dispatch.append(cleaned_df_dispatch)

    # Unimos todos los dfs del área de capacidades en uno solo
    unified_df_capacity = pd.concat(
        objs=cleaned_dfs_capacity,
        ignore_index=True,
    )
    unified_df_capacity = normalize_date(
        df=unified_df_capacity,
        column="Fecha",
        input_format="dd/mm/yy",
    )

    # Unimos todos los archivos del área de despacho en uno solo
    unified_df_dispatch = pd.concat(
        objs=cleaned_dfs_dispatch,
        ignore_index=True,
    )
    unified_df_dispatch = normalize_date(
        df=unified_df_dispatch,
        column="Fecha",
        input_format="mm/dd/yy",
    )

    # Unimos el df del área de capacidades y despacho en uno solo
    df_output = join(
        df1=unified_df_dispatch,
        df2=unified_df_capacity,
        foreign_key="Orden de trabajo",
        date_column="Fecha",
        time_column="Inicio",
    )

    # Renombramos los encabezados de df_output
    df_output.rename(columns=FINAL_COLUMNS, inplace=True)

    # Agregamos columnas para el análisis de las razones
    df_output["Estado de la Razón"] = None
    df_output["Razón Sugerida"] = None

    # Reordenamos las columnas
    df_output = reorder_columns(df=df_output, order=COLUMN_ORDER)

    # Creamos archivo de salida
    message = f"Creando archivo: {parameters.REASONED_ANALYSIS_FILE_PATH}"
    logging(message=message, level="INFO")

    create_file(df=df_output, path=parameters.REASONED_ANALYSIS_FILE_PATH)

    logging(message="Limpieza completada", level="INFO")

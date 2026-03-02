from copy import deepcopy

import pandas as pd

from config import parameters
from data.clean import (
    CleanDataFrame,
    clean_df_ofsc_capacity,
    clean_df_ofsc_dispatch,
    clean_df_residential_plant,
)
from data.operations import create_file, join, join_by_sales_advisor, read_excel
from logs_setup import get_time_stamp
from match_files import pair_files

RESIDENTIAL_PLANT_PATH = parameters.DATABASES_FOLDER / "RM Planta Residencial.xlsx"
OFSC_CAPACITY_FOLDER = parameters.DATABASES_FOLDER / "OFSC (capacidades)"
OFSC_DISPATCH_FOLDER = parameters.DATABASES_FOLDER / "OFSC (despacho)"


def main() -> None:

    result = pair_files(dir1=OFSC_CAPACITY_FOLDER, dir2=OFSC_DISPATCH_FOLDER)

    # Log init
    time_stamp = get_time_stamp()
    message = "Se van a limpiar los datos de los siguientes archivos:\n"

    message = message + "\nOFSC (CAPACIDADES):\n"
    only_in_dir1 = [paths[0] for paths in result.pairs]

    for file_path in only_in_dir1:
        message = message + f">> {file_path}\n"

    message = message + "\nOFSC (DESPACHO):\n"
    only_in_dir2 = [paths[-1] for paths in result.pairs]

    for file_path in only_in_dir2:
        message = message + f">> {file_path}\n"

    message = message + "\nPLANTA RESIDENCIAL:\n"
    message = message + f">> {RESIDENTIAL_PLANT_PATH}\n"
    print(f"{time_stamp} [ INFO ] {message}")
    # Log end

    dfs_residential_plant: list[pd.DataFrame] = []
    dfs_ofsc_capacity: list[pd.DataFrame] = []
    dfs_ofsc_dispatch: list[pd.DataFrame] = []

    try:
        # Log init
        time_stamp = get_time_stamp()
        message = f"Iniciando limpieza: {RESIDENTIAL_PLANT_PATH}"
        print(f"{time_stamp} [ INFO ] {message}")
        # Log end

        df_residential_plant = read_excel(path=RESIDENTIAL_PLANT_PATH, sheet=0)
        NEW_RESIDENTIAL_PLANT_COLUMNS: list[str] = []

        for path_ofsc_capacity_file, path_ofsc_dispatch_file in result.pairs:
            RESIDENTIAL_PLANT_COLUMNS = deepcopy(parameters.RESIDENTIAL_PLANT_COLUMNS)

            # Log init
            time_stamp = get_time_stamp()
            message = f"Iniciando limpieza: {path_ofsc_capacity_file}"
            print(f"{time_stamp} [ INFO ] {message}")
            # Log end

            df_ofsc_capacity = read_excel(path=path_ofsc_capacity_file, sheet=0)
            df_ofsc_capacity = clean_df_ofsc_capacity(df=df_ofsc_capacity)

            # Log init
            time_stamp = get_time_stamp()
            message = f"Iniciando limpieza: {path_ofsc_dispatch_file}"
            print(f"{time_stamp} [ INFO ] {message}")
            # Log end

            df_ofsc_dispatch = read_excel(path=path_ofsc_dispatch_file, sheet=0)
            df_ofsc_dispatch = clean_df_ofsc_dispatch(df=df_ofsc_dispatch)

            # Iniciamos a limpiar planta residencial
            df_residential_plant_copy = df_residential_plant.copy()
            df_residential_plant_copy = clean_df_residential_plant(
                df=df_residential_plant_copy,
                df_ofsc_capacity=df_ofsc_capacity,
            )

            # Renombramos columnas de planta residencial
            df_residential_plant_copy = df_residential_plant_copy.rename(
                columns={"NOMBRE": "Asesor comercial"}
            )

            index = 0

            for campo in parameters.RESIDENTIAL_PLANT_COLUMNS:
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

        # Unimos el OFSC de despacho y capacidades en uno solo
        # Log init
        time_stamp = get_time_stamp()
        message = "Uniendo todos los OFSC de despacho y capacidades..."
        print(f"{time_stamp} [ INFO ] {message}")
        # Log end

        df_ofsc_capacity = pd.concat(objs=dfs_ofsc_capacity, ignore_index=True)
        df_ofsc_dispatch = pd.concat(objs=dfs_ofsc_dispatch, ignore_index=True)

        if parameters.DEBUG:
            create_file(df=df_ofsc_capacity, path=parameters.CLEAN_OFSC_CAPACITY_PATH)
            create_file(df=df_ofsc_dispatch, path=parameters.CLEAN_OFSC_DISPATCH_PATH)

        df_ofsc = join(
            df1=df_ofsc_dispatch,
            df2=df_ofsc_capacity,
            foreign_key="Orden de trabajo",
            date_column="Fecha",
            columns_df1=parameters.OFSC_DISPATCH_COLUMNS,
            columns_df2=parameters.OFSC_CAPACITY_COLUMNS,
        )

        if parameters.DEBUG:
            create_file(df=df_ofsc, path=parameters.CLEAN_OFSC_PATH)

        # Unimos OFSC y Planta residencial en uno solo
        # Log init
        time_stamp = get_time_stamp()
        message = "Uniendo OFSC y Planta Residencial..."
        print(f"{time_stamp} [ INFO ] {message}")
        # Log end

        df_residential_plant = pd.concat(objs=dfs_residential_plant, ignore_index=True)
        df_residential_plant = CleanDataFrame.drop_duplicate_rows_by_column(
            df=df_residential_plant,
            column="Asesor comercial",
        )

        if parameters.DEBUG:
            create_file(
                df=df_residential_plant,
                path=parameters.CLEAN_RESIDENTIAL_PLANT_PATH,
            )

        df_output = join_by_sales_advisor(
            df=df_ofsc,
            df_dictionary=df_residential_plant,
        )
        df_output["Razón sugerida"] = None
        df_output["Estado del análisis"] = None

        # 9. Creamos la tabla final
        # Log init
        time_stamp = get_time_stamp()
        message = f"Creando: {parameters.OUTPUT_FILE_PATH}..."
        print(f"{time_stamp} [ INFO ] {message}")
        # Log end

        create_file(df=df_output, path=parameters.OUTPUT_FILE_PATH)
    except Exception as e:
        raise e

    # Log init
    time_stamp = get_time_stamp()
    message = "LIMPIEZA COMPLETADA."
    print(f"{time_stamp} [ INFO ] {message}")
    # Log end


if __name__ == "__main__":
    main()

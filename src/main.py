import sys
import traceback
from pathlib import Path

import pandas as pd

from config import parameters
from controllers import contact_analysis, efficacy_analysis, read_files
from data.match_files import pair_files
from data.operations import create_file
from logs_setup import logging

COMERCIAL_EFFICACY_ANALYSIS = parameters.COMERCIAL_EFFICACY_ANALYSIS
CONTACT_ANALYSIS = parameters.CONTACT_ANALYSIS


def __read_files(
    ofsc_capacity_files: list[Path],
    ofsc_dispatch_files: list[Path],
    residential_plant_file: Path,
) -> dict[str, list[pd.DataFrame] | pd.DataFrame]:
    message = "Se van a preparar los siguientes archivos, para los "
    message += ", ".join([COMERCIAL_EFFICACY_ANALYSIS, CONTACT_ANALYSIS])
    message += ".\n"
    message += "\nOFSC del del Área de Capacidades:\n"

    for path in ofsc_capacity_files:
        message += f"   >> {path}\n"

    message += "\nOFSC del Área de Despacho:\n"

    for path in ofsc_dispatch_files:
        message += f"   >> {path}\n"

    message += "\nPlanta Residencial:\n"
    message += f"   >> {parameters.RESIDENTIAL_PLANT_PATH}\n"

    logging(message=message, level="INFO")

    return read_files.read_files(
        ofsc_capacity_files=ofsc_capacity_files,
        ofsc_dispatch_files=ofsc_dispatch_files,
        residential_plant_file=residential_plant_file,
    )


def __commercial_effectiveness_analysis(
    df_residential_plant: pd.DataFrame,
    dfs_ofsc_capacity: list[pd.DataFrame],
    dfs_ofsc_dispatch: list[pd.DataFrame],
) -> None:
    message = f"Iniciando limpieza de los datos para el {COMERCIAL_EFFICACY_ANALYSIS}"
    logging(message=message, level="INFO")

    efficacy_analysis.clean_data(
        df_residential_plant=df_residential_plant,
        dfs_ofsc_capacity=dfs_ofsc_capacity,
        dfs_ofsc_dispatch=dfs_ofsc_dispatch,
    )

    logging(message="Limpieza completada.\n", level="INFO")


def __contact_analysis(
    df_residential_plant: pd.DataFrame,
    dfs_ofsc_capacity: list[pd.DataFrame],
) -> None:
    message = f"Iniciando limpieza de los datos para el {CONTACT_ANALYSIS}"
    logging(message=message, level="INFO")

    df_output = contact_analysis.clean_data(
        df_residential_plant=df_residential_plant,
        dfs_ofsc_capacity=dfs_ofsc_capacity,
    )

    logging(message="Limpieza completada.\n", level="INFO")

    df_output = contact_analysis.data_transformation(df=df_output)

    logging(
        message=f"Creando archivo final: {parameters.CONTACT_ANALYSIS_FILE_PATH}",
        level="INFO",
    )

    create_file(df=df_output, path=parameters.CONTACT_ANALYSIS_FILE_PATH)


def main() -> None:

    files_path = pair_files(
        dir1=parameters.OFSC_CAPACITY_FOLDER,
        dir2=parameters.OFSC_DISPATCH_FOLDER,
    )

    dfs = __read_files(
        ofsc_capacity_files=[paths[0] for paths in files_path.pairs],
        ofsc_dispatch_files=[paths[-1] for paths in files_path.pairs],
        residential_plant_file=parameters.RESIDENTIAL_PLANT_PATH,
    )

    df_residential_plant: pd.DataFrame = dfs["residential_plant"]  # type: ignore
    dfs_ofsc_capacity: list[pd.DataFrame] = dfs["ofsc_capacity"]  # type: ignore
    dfs_ofsc_dispatch: list[pd.DataFrame] = dfs["ofsc_dispatch"]  # type: ignore

    __commercial_effectiveness_analysis(
        df_residential_plant=df_residential_plant,
        dfs_ofsc_capacity=dfs_ofsc_capacity,
        dfs_ofsc_dispatch=dfs_ofsc_dispatch,
    )
    __contact_analysis(
        df_residential_plant=df_residential_plant,
        dfs_ofsc_capacity=dfs_ofsc_capacity,
    )


if __name__ == "__main__":
    try:
        main()

        logging(message="Datos procesados correctamente.", level="INFO")

        print("Datos procesados correctamente.", flush=True)
        sys.exit(0)
    except Exception as e:
        logging(message="Ocurrió un error: \n", level="ERROR")

        print(f"{e}", flush=True)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

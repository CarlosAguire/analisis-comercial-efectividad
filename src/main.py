import sys
import traceback

import pandas as pd

from config import parameters
from logs_setup import logging
from modules.controllers import contact_analysis, efficacy_analysis
from modules.data.match_files import PairingResult, pair_files
from modules.data.operations import create_file, read_excel

COMERCIAL_EFFICACY_ANALYSIS = parameters.COMERCIAL_EFFICACY_ANALYSIS
COLUMNS_TO_RESERVE = parameters.COLUMNS_TO_RESERVE[COMERCIAL_EFFICACY_ANALYSIS]


def __commercial_effectiveness_analysis(
    df_residential_plant: pd.DataFrame,
    files_path: PairingResult,
) -> None:
    message = "Se va a iniciar los procesos de limpieza de los datos del reporte: "
    message += parameters.COMERCIAL_EFFICACY_ANALYSIS.upper()
    logging(message=message, level="INFO")

    message = "Se van a limpiar los datos de los siguientes archivos:\n"
    message = message + "\nOFSC (CAPACIDADES):\n"
    only_in_dir1 = [paths[0] for paths in files_path.pairs]

    for file_path in only_in_dir1:
        message = message + f">> {file_path}\n"

    message = message + "\nOFSC (DESPACHO):\n"
    only_in_dir2 = [paths[-1] for paths in files_path.pairs]

    for file_path in only_in_dir2:
        message = message + f">> {file_path}\n"

    message = message + "\nPLANTA RESIDENCIAL:\n"
    message = message + f">> {parameters.RESIDENTIAL_PLANT_PATH}\n"

    logging(message=message, level="INFO")

    efficacy_analysis.clean_data(
        df_residential_plant=df_residential_plant,
        files_path=files_path,
    )


def __contact_analysis(
    df_residential_plant: pd.DataFrame,
    files_path: PairingResult,
) -> None:
    message = "Se va a iniciar los procesos de limpieza de los datos del reporte: "
    message += parameters.CONTACT_ANALYSIS.upper()
    logging(message=message, level="INFO")

    message = "Se van a limpiar los datos de los siguientes archivos:\n"
    message = message + "\nOFSC (CAPACIDADES):\n"
    only_in_dir1 = [paths[0] for paths in files_path.pairs]

    for file_path in only_in_dir1:
        message = message + f">> {file_path}\n"

    message = message + "\nPLANTA RESIDENCIAL:\n"
    message = message + f">> {parameters.RESIDENTIAL_PLANT_PATH}\n"

    logging(message=message, level="INFO")

    df_output = contact_analysis.clean_data(
        df_residential_plant=df_residential_plant,
        files_path=only_in_dir1,
    )
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

    df_residential_plant = read_excel(path=parameters.RESIDENTIAL_PLANT_PATH, sheet=0)

    __commercial_effectiveness_analysis(
        df_residential_plant=df_residential_plant,
        files_path=files_path,
    )
    __contact_analysis(
        df_residential_plant=df_residential_plant,
        files_path=files_path,
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

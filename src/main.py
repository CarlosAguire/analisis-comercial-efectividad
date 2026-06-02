import argparse
import sys
import traceback
from datetime import date, timedelta

import pandas as pd

import controllers
from config import parameters
from logs_setup import logging
from operations.data_frame import (
    read_csv_file,
    read_xlsx_file,
)
from operations.files import filter_files_by_date, get_latest_file, process_file_folders
from operations.validations import (
    validate_csv,
    validate_duplicate_suffix,
    validate_exact_file_path,
    validate_file_dates,
    validate_xlsx,
)

REASONED_ANALYSIS = parameters.REASONED_ANALYSIS
PRODUCTIVITY_ANALYSIS = parameters.PRODUCTIVITY_ANALYSIS
CONTACT_ANALYSIS = parameters.CONTACT_ANALYSIS
BACKLOG_ANALYSIS = parameters.BACKLOG_ANALYSIS
MIGRATIONS_ANALYSIS = parameters.MIGRATIONS_ANALYSIS


def __run_validations() -> None:
    """Ejecuta todas las validaciones necesarias antes de procesar los datos."""

    message = "Ejecutando validaciones estructurales y de formato."
    logging(message=message, level="INFO")

    # Validamos que los archivos tengan extensión .xlsx
    validate_xlsx(folder_path=parameters.FTTH_HFC_CAPACITY_FOLDER)
    validate_xlsx(folder_path=parameters.FTTH_HFC_DISPATCH_FOLDER)
    validate_xlsx(folder_path=parameters.FO_FOLDER)

    # Validamos que los archivos tengan extensión .csv
    validate_csv(folder_path=parameters.BACKLOG_FOLDER)

    # Validamos que los archivos no tengan sufijos de duplicado generados por Windows
    validate_duplicate_suffix(folder_path=parameters.FTTH_HFC_CAPACITY_FOLDER)
    validate_duplicate_suffix(folder_path=parameters.FTTH_HFC_DISPATCH_FOLDER)
    validate_duplicate_suffix(folder_path=parameters.FO_FOLDER)

    # Validamos que los archivos tengan fechas válidas en su nombre según el formato esperado
    validate_file_dates(
        folder_path=parameters.FTTH_HFC_CAPACITY_FOLDER,
        date_format=parameters.FTTH_HFC_CAPACITY_DATE_FORMAT,
    )
    validate_file_dates(
        folder_path=parameters.FTTH_HFC_DISPATCH_FOLDER,
        date_format=parameters.FTTH_HFC_DISPATCH_DATE_FORMAT,
    )
    validate_file_dates(
        folder_path=parameters.FO_FOLDER,
        date_format=parameters.FO_DATE_FORMAT,
    )

    # Validamos que archivos existan exactamente con el nombre y extensión esperados
    validate_exact_file_path(path=parameters.RESIDENTIAL_PLANT_PATH)
    validate_exact_file_path(path=parameters.GPON_BASES_PATH)
    validate_exact_file_path(path=parameters.BROWNFIELD_BASES_PATH)

    message = "Validaciones estructurales y de formato completadas exitosamente."
    logging(message=message, level="INFO")


def __run_analysis(
    productivity_analysis: bool,
    reasoned_analysis: bool,
    contact_analysis: bool,
    backlog_analysis: bool,
    migrations_analysis: bool,
) -> None:

    catalog_result = process_file_folders(
        ftth_hfc_capacity_folder=parameters.FTTH_HFC_CAPACITY_FOLDER,
        ftth_hfc_dispatch_folder=parameters.FTTH_HFC_DISPATCH_FOLDER,
        fo_folder=parameters.FO_FOLDER,
        date_format_ftth_hfc_capacity_folder=parameters.FTTH_HFC_CAPACITY_DATE_FORMAT,
        date_format_ftth_hfc_dispatch_folder=parameters.FTTH_HFC_DISPATCH_DATE_FORMAT,
        date_format_fo_folder=parameters.FO_DATE_FORMAT,
    )

    # Lista de DF que se usaran en otros análisis
    dfs_capacity: list[pd.DataFrame] = []

    if reasoned_analysis or contact_analysis or backlog_analysis:
        # Creamos DF del archivo de planta residencial
        df_residential_plant = read_csv_file(
            path=parameters.RESIDENTIAL_PLANT_PATH,
            dtype=parameters.RESIDENTIAL_PLANT_TYPES,
        )
        df_residential_plant.attrs["file_path"] = parameters.RESIDENTIAL_PLANT_PATH

        if backlog_analysis:
            # Creamos DF del archivo del backlog
            file_path_backlog = get_latest_file(folder_path=parameters.BACKLOG_FOLDER)
            df_backlog = read_csv_file(
                path=file_path_backlog,
                dtype=parameters.BACKLOG_TYPES,
            )
            df_backlog.attrs["file_path"] = file_path_backlog

            # Creamos DF del archivo de capacidades del arbol FTTH-HFC
            file_path_ftth_hfc = filter_files_by_date(
                inventory=catalog_result.files_by_date_ftth_hfc_capacity_folder,
                exact_date=date.today(),
            )[0]
            df_ftth_hfc = read_xlsx_file(
                dtype=parameters.FTTH_HFC_CAPACITY_TYPES,
                path=file_path_ftth_hfc,
                sheet=0,
            )
            df_ftth_hfc.attrs["file_path"] = file_path_ftth_hfc

            # Creamos DF del archivo del arbol FO
            file_path_fo = filter_files_by_date(
                inventory=catalog_result.files_by_date_fo_folder,
                exact_date=date.today(),
            )[0]
            df_fo = read_xlsx_file(
                dtype=parameters.FO_TYPES,
                path=file_path_fo,
                sheet=0,
            )
            df_fo.attrs["file_path"] = file_path_fo

            controllers.run_backlog_analysis(
                df_residential_plant=df_residential_plant,
                df_backlog=df_backlog,
                df_ftth_hfc=df_ftth_hfc,
                df_fo=df_fo,
            )

            # Si no se requieren los otros análisis, se termina la función aquí
            if (
                backlog_analysis
                and not contact_analysis
                and not reasoned_analysis
                and not productivity_analysis
                and not migrations_analysis
            ):
                return None
        if reasoned_analysis:
            files_path_ftth_hfc_capacity = filter_files_by_date(
                inventory=catalog_result.files_by_date_ftth_hfc_capacity_folder,
                end_date=date.today() - timedelta(days=1),
            )

            for file_path in files_path_ftth_hfc_capacity:
                df_capacity = read_xlsx_file(
                    dtype=parameters.FTTH_HFC_CAPACITY_TYPES,
                    path=file_path,
                    sheet=0,
                )
                df_capacity.attrs["file_path"] = file_path
                dfs_capacity.append(df_capacity)

            files_path_ftth_hfc_dispatch = filter_files_by_date(
                inventory=catalog_result.files_by_date_ftth_hfc_dispatch_folder,
                end_date=date.today() - timedelta(days=1),
            )

            dfs_dispatch: list[pd.DataFrame] = []

            for file_path in files_path_ftth_hfc_dispatch:
                df_dispatch = read_xlsx_file(
                    dtype=parameters.FTTH_HFC_DISPATCH_TYPES,
                    path=file_path,
                    sheet=0,
                )
                df_dispatch.attrs["file_path"] = file_path
                dfs_dispatch.append(df_dispatch)

            controllers.run_reasoned_analysis(
                df_residential_plant=df_residential_plant,
                dfs_capacity=dfs_capacity,
                dfs_dispatch=dfs_dispatch,
            )

            # Si no se requieren los otros análisis, se termina la función aquí
            if (
                reasoned_analysis
                and not contact_analysis
                and not productivity_analysis
                and not migrations_analysis
                and not backlog_analysis
            ):
                return None
        if contact_analysis:
            if not dfs_capacity:
                files_path_ftth_hfc_capacity = filter_files_by_date(
                    inventory=catalog_result.files_by_date_ftth_hfc_capacity_folder,
                    end_date=date.today() - timedelta(days=1),
                )

                for file_path in files_path_ftth_hfc_capacity:
                    df_capacity = read_xlsx_file(
                        dtype=parameters.FTTH_HFC_CAPACITY_TYPES,
                        path=file_path,
                        sheet=0,
                    )
                    df_capacity.attrs["file_path"] = file_path
                    dfs_capacity.append(df_capacity)

            controllers.run_contact_analysis(
                df_residential_plant=df_residential_plant,
                dfs_capacity=dfs_capacity,
            )

            # Si no se requieren los otros análisis, se termina la función aquí
            if (
                contact_analysis
                and not reasoned_analysis
                and not productivity_analysis
                and not migrations_analysis
                and not backlog_analysis
            ):
                return None
    if productivity_analysis:
        if not dfs_capacity:
            files_path_ftth_hfc_capacity = filter_files_by_date(
                inventory=catalog_result.files_by_date_ftth_hfc_capacity_folder,
                end_date=date.today() - timedelta(days=1),
            )

            for file_path in files_path_ftth_hfc_capacity:
                df_capacity = read_xlsx_file(
                    dtype=parameters.FTTH_HFC_CAPACITY_TYPES,
                    path=file_path,
                    sheet=0,
                )
                df_capacity.attrs["file_path"] = file_path
                dfs_capacity.append(df_capacity)

        dfs_ftth_hfc = dfs_capacity
        dfs_fo = []

        files_path_fo = filter_files_by_date(
            inventory=catalog_result.files_by_date_fo_folder,
            end_date=date.today() - timedelta(days=1),
        )

        for file_path in files_path_fo:
            df_fo = read_xlsx_file(path=file_path, sheet=0, dtype=parameters.FO_TYPES)
            df_fo.attrs["file_path"] = file_path
            dfs_fo.append(df_fo)

        controllers.run_productivity_analysis(dfs_ftth_hfc=dfs_ftth_hfc, dfs_fo=dfs_fo)

        # Si no se requieren los otros análisis, se termina la función aquí
        if (
            productivity_analysis
            and not reasoned_analysis
            and not contact_analysis
            and not migrations_analysis
            and not backlog_analysis
        ):
            return None
    if migrations_analysis:
        df_gpon = read_xlsx_file(
            path=parameters.GPON_BASES_PATH,
            dtype=parameters.GPON_TYPES,
            sheet="TOTAL",
        )
        df_gpon.attrs["file_path"] = parameters.GPON_BASES_PATH
        df_brownfield = read_xlsx_file(
            path=parameters.BROWNFIELD_BASES_PATH,
            sheet="BASE BROWNFIELD 2025(BASE)",
            dtype=parameters.BROWNFIELD_TYPES,
        )
        df_brownfield.attrs["file_path"] = parameters.BROWNFIELD_BASES_PATH

        controllers.run_migrations_analysis(
            df_gpon=df_gpon,
            df_brownfield=df_brownfield,
        )

        # Si no se requieren los otros análisis, se termina la función aquí
        if (
            migrations_analysis
            and not reasoned_analysis
            and not contact_analysis
            and not productivity_analysis
            and not backlog_analysis
        ):
            return None

    logging(message="Datos procesados correctamente.", level="INFO")
    print("Datos procesados correctamente.", flush=True)

    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reasoned", action="store_true")
    parser.add_argument("--contact", action="store_true")
    parser.add_argument("--backlog", action="store_true")
    parser.add_argument("--productivity", action="store_true")
    parser.add_argument("--migrations", action="store_true")
    args = parser.parse_args()

    try:
        reasoned_analysis = args.reasoned
        contact_analysis = args.contact
        backlog_analysis = args.backlog
        productivity_analysis = args.productivity
        migrations_analysis = args.migrations
        analysis_to_run = []

        if reasoned_analysis:
            analysis_to_run.append(f"\n    >> {REASONED_ANALYSIS}")
        if contact_analysis:
            analysis_to_run.append(f"\n    >> {CONTACT_ANALYSIS}")
        if backlog_analysis:
            analysis_to_run.append(f"\n    >> {BACKLOG_ANALYSIS}")
        if productivity_analysis:
            analysis_to_run.append(f"\n    >> {PRODUCTIVITY_ANALYSIS}")
        if migrations_analysis:
            analysis_to_run.append(f"\n    >> {MIGRATIONS_ANALYSIS}")

        # Ejecutamos análisis solicitados
        message = "Preparando archivos para ejecutar los siguientes análisis:"
        message += "".join(analysis_to_run)
        logging(message=message, level="INFO")

        __run_validations()
        __run_analysis(
            productivity_analysis=productivity_analysis,
            reasoned_analysis=reasoned_analysis,
            contact_analysis=contact_analysis,
            backlog_analysis=backlog_analysis,
            migrations_analysis=migrations_analysis,
        )

        sys.exit(0)
    except Exception as e:
        logging(message="Ocurrió un error:\n", level="ERROR")
        print(f"{e}", flush=True)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

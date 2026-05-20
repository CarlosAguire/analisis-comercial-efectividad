import argparse
import sys
import traceback
from datetime import date

from config import parameters
from logs_setup import logging
from operations.data_frame import read_csv_file, read_xlsb_file, read_xlsx_file
from operations.files import filter_files_by_date, get_latest_file, process_file_folders
from src import controllers

REASONED_ANALYSIS = parameters.REASONED_ANALYSIS
PRODUCTIVITY_ANALYSIS = parameters.PRODUCTIVITY_ANALYSIS
CONTACT_ANALYSIS = parameters.CONTACT_ANALYSIS
BACKLOG_ANALYSIS = parameters.BACKLOG_ANALYSIS
BACKLOG_ONNET_ANALYSIS = parameters.BACKLOG_ONNET_ANALYSIS
MIGRATIONS_ANALYSIS = parameters.MIGRATIONS_ANALYSIS

FTTH_HFC_CAPACITY_FOLDER = parameters.FTTH_HFC_FOLDER / "Capacidades"
FTTH_HFC_DISPATCH_FOLDER = parameters.FTTH_HFC_FOLDER / "Despacho"


def run_analysis(
    productivity_analysis: bool,
    reasoned_analysis: bool,
    contact_analysis: bool,
    backlog_analysis: bool,
    backlog_onnet_analysis: bool,
    migrations_analysis: bool,
) -> None:

    catalog_result = process_file_folders(
        ftth_hfc_capacity_folder=FTTH_HFC_CAPACITY_FOLDER,
        ftth_hfc_dispatch_folder=FTTH_HFC_DISPATCH_FOLDER,
        fo_folder=parameters.FO_FOLDER,
        date_format_ftth_hfc_capacity_folder="dmy",
        date_format_ftth_hfc_dispatch_folder="mdy",
        date_format_fo_folder="dmy",
    )

    dfs_ftth_hfc_tree = []

    if (
        reasoned_analysis
        or contact_analysis
        or backlog_analysis
        or backlog_onnet_analysis
    ):
        # Creamos DF del archivo de planta residencial
        df_residential_plant = read_xlsb_file(
            path=parameters.RESIDENTIAL_PLANT_PATH,
            sheet=1,
        )
        df_residential_plant.attrs["file_path"] = parameters.RESIDENTIAL_PLANT_PATH

        if backlog_analysis:
            # Creamos DF del archivo del backlog
            file_path_backlog = get_latest_file(folder_path=parameters.BACKLOG_FOLDER)
            df_backlog = read_csv_file(path=file_path_backlog)
            df_backlog.attrs["file_path"] = file_path_backlog

            # Creamos DF del archivo de capacidades del arbol FTTH-HFC
            file_path_ftth_hfc = filter_files_by_date(
                inventory=catalog_result.files_by_date_ftth_hfc_capacity_folder,
                exact_date=date.today(),
            )[0]
            df_ftth_hfc = read_xlsx_file(path=file_path_ftth_hfc, sheet=0)
            df_ftth_hfc.attrs["file_path"] = file_path_ftth_hfc

            # Creamos DF del archivo del arbol FO
            file_path_fo = filter_files_by_date(
                inventory=catalog_result.files_by_date_fo_folder,
                exact_date=date.today(),
            )[0]
            df_fo = read_xlsx_file(path=file_path_fo, sheet=0)
            df_fo.attrs["file_path"] = file_path_fo

            controllers.run_backlog_analysis(
                df_residential_plant=df_residential_plant,
                df_backlog=df_backlog,  # type: ignore
                dfs_ofsc_capacity=dfs_capacity,
                dfs_ofsc=dfs_ofsc,
            )

            # Si no se requieren los otros análisis, se termina la función aquí
            if (
                backlog_analysis_parameter
                and not contact_analysis_parameter
                and not productivity_analysis_parameter
                and not migrations_analysis_parameter
                and not commercial_analysis_parameter
            ):
                return None

        dfs_capacity = []

        for capacity_file_path in [paths[0] for paths in file_paths.pairs]:
            df_capacity = read_xlsx_file(path=capacity_file_path, sheet=0)
            df_capacity.attrs["path"] = capacity_file_path
            dfs_capacity.append(df_capacity)

        if productivity_analysis_parameter:
            dfs_ftth_hfc_tree = dfs_capacity

        if commercial_analysis_parameter:
            dfs_dispatch = []

            for dispatch_file_path in [paths[-1] for paths in file_paths.pairs]:
                df_dispatch = read_xlsx_file(path=dispatch_file_path, sheet=0)
                df_dispatch.attrs["path"] = dispatch_file_path
                dfs_dispatch.append(df_dispatch)

            commercial_analysis.run(
                df_residential_plant=df_residential_plant,
                dfs_ofsc_capacity=dfs_capacity,
                dfs_ofsc_dispatch=dfs_dispatch,
            )

            # Si no se requieren los otros análisis, se termina la función aquí
            if (
                commercial_analysis_parameter
                and not contact_analysis_parameter
                and not productivity_analysis_parameter
                and not migrations_analysis_parameter
                and not backlog_analysis_parameter
            ):
                return None
        if contact_analysis_parameter:
            contact_analysis.run(
                df_residential_plant=df_residential_plant,
                dfs_ofsc_capacity=dfs_capacity,
            )

            # Si no se requieren los otros análisis, se termina la función aquí
            if (
                contact_analysis_parameter
                and not commercial_analysis_parameter
                and not productivity_analysis_parameter
                and not migrations_analysis_parameter
                and not backlog_analysis_parameter
            ):
                return None
    if productivity_analysis_parameter:
        dfs_fo_tree = []

        for file_path in [
            path for path in FO_CAPACITY_FOLDER.iterdir() if path.is_file()
        ]:
            df = read_xlsx_file(path=file_path, sheet=0)
            df.attrs["path"] = file_path
            dfs_fo_tree.append(df)

        productivity_analysis.run(ftth_hfc_tree=dfs_ftth_hfc_tree, fo_tree=dfs_fo_tree)

        # Si no se requieren los otros análisis, se termina la función aquí
        if (
            productivity_analysis_parameter
            and not commercial_analysis_parameter
            and not contact_analysis_parameter
            and not migrations_analysis_parameter
            and not backlog_analysis_parameter
        ):
            return None
    if migrations_analysis_parameter:
        df_gpon = read_xlsx_file(
            path=parameters.GPON_BASES_PATH,
            sheet="TOTAL",
        )
        df_brownfield = read_xlsx_file(
            path=parameters.BROWNFIELD_BASES_PATH,
            sheet="BASE BROWNFIELD 2025(BASE)",
        )

        migrations_analysis.run(df_gpon=df_gpon, df_brownfield=df_brownfield)

        # Si no se requieren los otros análisis, se termina la función aquí
        if (
            migrations_analysis_parameter
            and not commercial_analysis_parameter
            and not contact_analysis_parameter
            and not productivity_analysis_parameter
            and not backlog_analysis_parameter
        ):
            return None

    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reasoned", action="store_true")
    parser.add_argument("--contact", action="store_true")
    parser.add_argument("--backlog", action="store_true")
    parser.add_argument("--backlog_onnet", action="store_true")
    parser.add_argument("--productivity", action="store_true")
    parser.add_argument("--migrations", action="store_true")
    args = parser.parse_args()

    try:
        reasoned_analysis = args.reasoned
        contact_analysis = args.contact
        backlog_analysis = args.backlog
        backlog_onnet_analysis = args.backlog_onnet
        productivity_analysis = args.productivity
        migrations_analysis = args.migrations
        analysis_to_run = []

        if reasoned_analysis:
            analysis_to_run.append(f"\n    >> {REASONED_ANALYSIS}")
        if contact_analysis:
            analysis_to_run.append(f"\n    >> {CONTACT_ANALYSIS}")
        if backlog_analysis:
            analysis_to_run.append(f"\n    >> {BACKLOG_ANALYSIS}")
        if backlog_onnet_analysis:
            analysis_to_run.append(f"\n    >> {BACKLOG_ONNET_ANALYSIS}")
        if productivity_analysis:
            analysis_to_run.append(f"\n    >> {PRODUCTIVITY_ANALYSIS}")
        if migrations_analysis:
            analysis_to_run.append(f"\n    >> {MIGRATIONS_ANALYSIS}")

        message = "Preparando archivos para ejecutar los siguientes análisis:"
        message += "".join(analysis_to_run)
        logging(message=message, level="INFO")

        # Ejecutamos análisis solicitados
        run_analysis(
            productivity_analysis=productivity_analysis,
            reasoned_analysis=reasoned_analysis,
            contact_analysis=contact_analysis,
            backlog_analysis=backlog_analysis,
            backlog_onnet_analysis=backlog_onnet_analysis,
            migrations_analysis=migrations_analysis,
        )

        logging(message="Datos procesados correctamente.", level="INFO")
        print("Datos procesados correctamente.", flush=True)
        sys.exit(0)
    except Exception as e:
        logging(message="Ocurrió un error:\n", level="ERROR")
        print(f"{e}", flush=True)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

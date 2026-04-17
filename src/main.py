import argparse
import sys
import traceback

from config import parameters
from controllers import (
    backlog_analysis,
    commercial_analysis,
    contact_analysis,
    migrations_analysis,
    productivity_analysis,
)
from data.match_files import pair_files
from data.operations import read_csv_file, read_xlsb_file, read_xlsx_file
from logs_setup import logging

COMERCIAL_EFFICACY_ANALYSIS = parameters.COMERCIAL_EFFICACY_ANALYSIS
PRODUCTIVITY_ANALYSIS = parameters.PRODUCTIVITY_ANALYSIS
CONTACT_ANALYSIS = parameters.CONTACT_ANALYSIS
BACKLOG_ANALYSIS = parameters.BACKLOG_ANALYSIS

FTTH_HFC_TREE_FOLDER = parameters.FTTH_HFC_TREE_FOLDER
FTTH_HFC_CAPACITY_FOLDER = FTTH_HFC_TREE_FOLDER / "OFSC" / "Area de Capacidades"
FTTH_HFC_DISPATCH_FOLDER = FTTH_HFC_TREE_FOLDER / "OFSC" / "Area de Despacho"

FO_CAPACITY_FOLDER = parameters.FO_TREE_FOLDER / "OFSC"


def run_analysis(
    productivity_analysis_parameter: bool,
    commercial_analysis_parameter: bool,
    contact_analysis_parameter: bool,
    backlog_analysis_parameter: bool,
    migrations_analysis_parameter: bool,
) -> None:

    dfs_ftth_hfc_tree = []

    if (
        commercial_analysis_parameter
        or contact_analysis_parameter
        or backlog_analysis_parameter
    ):
        df_residential_plant = read_xlsx_file(
            path=parameters.RESIDENTIAL_PLANT_PATH,
            sheet=1,
        )
        df_residential_plant.attrs["path"] = parameters.RESIDENTIAL_PLANT_PATH

        if backlog_analysis_parameter:
            df_backlog = read_csv_file(path=parameters.BACKLOG_PATH)
            df_backlog.attrs["path"] = parameters.BACKLOG_PATH

            backlog_analysis.run(
                df_residential_plant=df_residential_plant,
                df_backlog=df_backlog,
            )

            # Si no se requieren los otros análisis, se termina la función aquí
            if not (
                commercial_analysis_parameter
                and contact_analysis_parameter
                and productivity_analysis_parameter
                and migrations_analysis_parameter
            ):
                return None

        file_paths = pair_files(
            dir1=FTTH_HFC_CAPACITY_FOLDER,
            dir2=FTTH_HFC_DISPATCH_FOLDER,
        )

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
            if not (
                backlog_analysis_parameter
                and contact_analysis_parameter
                and productivity_analysis_parameter
                and migrations_analysis_parameter
            ):
                return None
        if contact_analysis_parameter:
            contact_analysis.run(
                df_residential_plant=df_residential_plant,
                dfs_ofsc_capacity=dfs_capacity,
            )

            # Si no se requieren los otros análisis, se termina la función aquí
            if not (
                backlog_analysis_parameter
                and commercial_analysis_parameter
                and productivity_analysis_parameter
                and migrations_analysis_parameter
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
        if not (
            backlog_analysis_parameter
            and commercial_analysis_parameter
            and contact_analysis_parameter
            and migrations_analysis_parameter
        ):
            return None
    if migrations_analysis_parameter:
        df_gpon = read_xlsx_file(
            path=parameters.GPON_BASES_PATH,
            sheet="TOTAL",
        )
        df_brownfield = read_xlsb_file(
            path=parameters.BROWNFIELD_BASES_PATH,
            sheet="BASE BROWNFIELD 2025(BASE)",
        )

        migrations_analysis.run(df_gpon=df_gpon, df_brownfield=df_brownfield)

        # Si no se requieren los otros análisis, se termina la función aquí
        if not (
            backlog_analysis_parameter
            and commercial_analysis_parameter
            and contact_analysis_parameter
            and productivity_analysis_parameter
        ):
            return None

    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--commercial_analysis", action="store_true")
    parser.add_argument("--contact_analysis", action="store_true")
    parser.add_argument("--backlog_analysis", action="store_true")
    parser.add_argument("--productivity_analysis", action="store_true")
    parser.add_argument("--migrations_analysis", action="store_true")
    args = parser.parse_args()

    try:
        commercial_analysis_parameter = args.commercial_analysis
        contact_analysis_parameter = args.contact_analysis
        backlog_analysis_parameter = args.backlog_analysis
        productivity_analysis_parameter = args.productivity_analysis
        migrations_analysis_parameter = args.migrations_analysis

        run_analysis(
            productivity_analysis_parameter=productivity_analysis_parameter,
            commercial_analysis_parameter=commercial_analysis_parameter,
            contact_analysis_parameter=contact_analysis_parameter,
            backlog_analysis_parameter=backlog_analysis_parameter,
            migrations_analysis_parameter=migrations_analysis_parameter,
        )

        logging(message="Datos procesados correctamente.", level="INFO")

        print("Datos procesados correctamente.", flush=True)
        sys.exit(0)
    except Exception as e:
        logging(message="Ocurrió un error:\n", level="ERROR")

        print(f"{e}", flush=True)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

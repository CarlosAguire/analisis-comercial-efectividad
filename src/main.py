import argparse
import sys
import traceback
from pathlib import Path

import pandas as pd

from config import parameters
from controllers import (
    backlog_analysis,
    commercial_analysis,
    contact_analysis,
    productivity_analysis,
    read_files,
)
from data.match_files import pair_files
from logs_setup import logging

COMERCIAL_EFFICACY_ANALYSIS = parameters.COMERCIAL_EFFICACY_ANALYSIS
PRODUCTIVITY_ANALYSIS = parameters.PRODUCTIVITY_ANALYSIS
CONTACT_ANALYSIS = parameters.CONTACT_ANALYSIS
BACKLOG_ANALYSIS = parameters.BACKLOG_ANALYSIS


def __read_files(
    ofsc_capacity_files: list[Path],
    ofsc_dispatch_files: list[Path],
    residential_plant_file: Path | None,
    backlog_dir: Path,
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

    if residential_plant_file:
        message += "\nPlanta Residencial:\n"
        message += f"   >> {residential_plant_file}\n"

    logging(message=message, level="INFO")

    backlog_file = [p for p in backlog_dir.iterdir() if p.is_file()][0]

    return read_files.read_files(
        ofsc_capacity_files=ofsc_capacity_files,
        ofsc_dispatch_files=ofsc_dispatch_files,
        residential_plant_file=residential_plant_file,
        backlog_file=backlog_file,
    )


def run_analysis(
    productivity_analysis_parameter: bool,
    commercial_analysis_parameter: bool,
    contact_analysis_parameter: bool,
    backlog_analysis_parameter: bool,
) -> None:
    FTTH_HFC_TREE_FOLDER = parameters.FTTH_HFC_TREE_FOLDER
    OFSC_CAPACITY_FOLDER = FTTH_HFC_TREE_FOLDER / "OFSC" / "Area de Capacidades"
    OFSC_DISPATCH_FOLDER = FTTH_HFC_TREE_FOLDER / "OFSC" / "Area de Despacho"

    files_path = pair_files(
        dir1=OFSC_CAPACITY_FOLDER,
        dir2=OFSC_DISPATCH_FOLDER,
    )

    conditon = (
        productivity_analysis_parameter
        and not commercial_analysis_parameter
        and not contact_analysis_parameter
        and not backlog_analysis_parameter
    )

    dfs = __read_files(
        ofsc_capacity_files=[paths[0] for paths in files_path.pairs],
        ofsc_dispatch_files=[paths[-1] for paths in files_path.pairs],
        residential_plant_file=None if conditon else parameters.RESIDENTIAL_PLANT_PATH,
        backlog_dir=parameters.BACKLOG_FOLDER,
    )

    df_residential_plant: pd.DataFrame = dfs["residential_plant"]  # type: ignore
    df_backlog: pd.DataFrame = dfs["backlog"]  # type: ignore
    dfs_ofsc_capacity: list[pd.DataFrame] = dfs["ofsc_capacity"]  # type: ignore
    dfs_ofsc_dispatch: list[pd.DataFrame] = dfs["ofsc_dispatch"]  # type: ignore

    if commercial_analysis_parameter:
        commercial_analysis.run(
            df_residential_plant=df_residential_plant,
            dfs_ofsc_capacity=dfs_ofsc_capacity,
            dfs_ofsc_dispatch=dfs_ofsc_dispatch,
        )
    if contact_analysis_parameter:
        contact_analysis.run(
            df_residential_plant=df_residential_plant,
            dfs_ofsc_capacity=dfs_ofsc_capacity,
        )
    if backlog_analysis_parameter:
        backlog_analysis.run(
            df_residential_plant=df_residential_plant,
            df_backlog=df_backlog,
        )

    OFSC_FOLDER = parameters.FO_TREE_FOLDER / "OFSC"

    data = {"ftth_hfc_tree": dfs}
    dfs = read_files.read_files(
        ofsc_capacity_files=[p for p in OFSC_FOLDER.iterdir() if p.is_file()],
        ofsc_dispatch_files=None,
        residential_plant_file=None,
        backlog_file=None,
    )
    data["fo_tree"] = dfs

    dfs_ftth_hfc_tree: list[pd.DataFrame]
    dfs_ftth_hfc_tree = data["ftth_hfc_tree"]["ofsc_capacity"]  # type: ignore
    dfs_fo_tree: list[pd.DataFrame]
    dfs_fo_tree = data["fo_tree"]["ofsc_capacity"]  # type: ignore

    if productivity_analysis_parameter:
        productivity_analysis.run(ftth_hfc_tree=dfs_ftth_hfc_tree, fo_tree=dfs_fo_tree)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--commercial_analysis", action="store_true")
    parser.add_argument("--contact_analysis", action="store_true")
    parser.add_argument("--backlog_analysis", action="store_true")
    parser.add_argument("--productivity_analysis", action="store_true")
    args = parser.parse_args()

    try:
        commercial_analysis_parameter = args.commercial_analysis
        contact_analysis_parameter = args.contact_analysis
        backlog_analysis_parameter = args.backlog_analysis
        productivity_analysis_parameter = args.productivity_analysis

        run_analysis(
            productivity_analysis_parameter=productivity_analysis_parameter,
            commercial_analysis_parameter=commercial_analysis_parameter,
            contact_analysis_parameter=contact_analysis_parameter,
            backlog_analysis_parameter=backlog_analysis_parameter,
        )

        logging(message="Datos procesados correctamente.", level="INFO")

        print("Datos procesados correctamente.", flush=True)
        sys.exit(0)
    except Exception as e:
        logging(message="Ocurrió un error: \n", level="ERROR")

        print(f"{e}", flush=True)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

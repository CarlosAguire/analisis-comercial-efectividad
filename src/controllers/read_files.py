from pathlib import Path

import pandas as pd

from data.operations import read_csv_file, read_xlsx_file
from logs_setup import logging


def __get_list_df(
    files_path: list[Path] | None,
    sheet: int | str,
) -> list[pd.DataFrame]:

    list_df = []

    if not files_path:
        return list_df

    for path in files_path:
        df = read_xlsx_file(path=path, sheet=sheet)
        df.attrs["path"] = path
        list_df.append(df)

    return list_df


def read_files(
    ofsc_capacity_files: list[Path] | None,
    ofsc_dispatch_files: list[Path] | None,
    residential_plant_file: Path | None,
    backlog_file: Path | None,
) -> dict[str, list[pd.DataFrame] | pd.DataFrame]:

    df_residential_plant = None
    df_backlog = None

    if residential_plant_file:
        df_residential_plant = read_xlsx_file(path=residential_plant_file, sheet=1)
        df_residential_plant.attrs["path"] = residential_plant_file
    if backlog_file:
        df_backlog = read_csv_file(path=backlog_file)
        df_backlog.attrs["path"] = backlog_file

    dfs = {
        "ofsc_capacity": __get_list_df(files_path=ofsc_capacity_files, sheet=0),
        "ofsc_dispatch": __get_list_df(files_path=ofsc_dispatch_files, sheet=0),
        "residential_plant": df_residential_plant,
        "backlog": df_backlog,
    }

    logging(message="Se leyeron todos los archivos correctamente", level="INFO")

    return dfs

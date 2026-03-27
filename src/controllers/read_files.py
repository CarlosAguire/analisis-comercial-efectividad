from pathlib import Path

import pandas as pd

from data.operations import read_excel
from logs_setup import logging


def __get_list_df(files_path: list[Path], sheet: int | str) -> list[pd.DataFrame]:

    list_df = []

    for path in files_path:
        df = read_excel(path=path, sheet=sheet)
        df.attrs["path"] = path
        list_df.append(df)

    return list_df


def read_files(
    ofsc_capacity_files: list[Path],
    ofsc_dispatch_files: list[Path],
    residential_plant_file: Path,
) -> dict[str, list[pd.DataFrame] | pd.DataFrame]:
    df_residential_plant = read_excel(path=residential_plant_file, sheet=1)
    df_residential_plant.attrs["path"] = residential_plant_file

    dfs = {
        "ofsc_capacity": __get_list_df(files_path=ofsc_capacity_files, sheet=0),
        "ofsc_dispatch": __get_list_df(files_path=ofsc_dispatch_files, sheet=0),
        "residential_plant": df_residential_plant,
    }

    logging(message="Se leyeron todos los archivos correctamente", level="INFO")

    return dfs

import pandas as pd

from config import parameters
from logs_setup import logging
from operations.data_frame import create_file

PRODUCTIVITY_ANALYSIS = parameters.PRODUCTIVITY_ANALYSIS


def __clean_data(dfs: list[pd.DataFrame]) -> pd.DataFrame:
    cleaned_dfs: list[pd.DataFrame] = []

    for df in dfs:
        logging(
            message=f"Iniciando limpieza: {df.attrs['path']}",
            level="INFO",
        )

        df_copy = df.copy()
        cleaned_dfs.append(df_copy)

    cleaned_df = pd.concat(
        objs=cleaned_dfs,
        ignore_index=True,
    )

    return cleaned_df


def run(ftth_hfc_tree: list[pd.DataFrame], fo_tree: list[pd.DataFrame]) -> None:
    # Iniciamos proceso de limpieza
    message = f"Preparando limpieza de los datos para el {PRODUCTIVITY_ANALYSIS}"
    logging(message=message, level="INFO")

    df_ftth_hfc_tree = __clean_data(dfs=ftth_hfc_tree)
    df_ftth_hfc_tree["Árbol"] = "FTTH y HFC"
    df_fo_tree = __clean_data(dfs=fo_tree)
    df_fo_tree["Árbol"] = "F.O."

    df_output = pd.concat(
        objs=[df_ftth_hfc_tree, df_fo_tree],
        ignore_index=True,
    )

    logging(message="Limpieza completada", level="INFO")
    logging(
        message=f"Creando archivo final: {parameters.PRODUCTIVITY_ANALYSIS_FILE_PATH}",
        level="INFO",
    )

    create_file(df=df_output, path=parameters.PRODUCTIVITY_ANALYSIS_FILE_PATH)

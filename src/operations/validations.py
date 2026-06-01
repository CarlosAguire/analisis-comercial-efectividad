import re
from pathlib import Path

import pandas as pd


def validate_xlsx(folder_path: Path) -> None:
    """
    Valida que todos los archivos dentro de una carpeta tengan extensión `.xlsx`.
    Recorre los archivos en la ruta proporcionada y lanza una excepción en el primer
    archivo que no cumpla con la condición.
    """

    for file in folder_path.iterdir():
        if file.is_file() and file.suffix.lower() != ".xlsx":
            raise ValueError(
                f"Validación fallida: se encontró un archivo con extensión no permitida.\n"
                f"Archivo: '{file.name}'\n"
                f"Extensión detectada: '{file.suffix or 'sin extensión'}'\n"
                f"Extensión esperada: '.xlsx'\n"
                f"Ruta: '{file.parent}'"
            )


def validate_duplicate_suffix(folder_path: Path) -> None:
    """
    Valida que ningún archivo dentro de una carpeta contenga sufijos de duplicado
    generados por Windows (por ejemplo: '(1)', '(2)', '(1) (1)', etc.) en su nombre.
    """

    # Detecta una o más ocurrencias de (n), incluso repetidas o separadas por espacios
    pattern = re.compile(r"(?:\(\d+\))+")

    for file in folder_path.iterdir():
        if file.is_file() and not file.name.startswith("~$"):
            matches = pattern.findall(file.stem)

            if matches:
                raise ValueError(
                    f"Validación fallida: se detectó un archivo con sufijo de duplicado.\n"
                    f"Archivo: '{file.name}'\n"
                    f"Nombre base: '{file.stem}'\n"
                    f"Sufijos detectados: {matches}\n"
                    f"Regla incumplida: no se permiten sufijos tipo '(n)' en los nombres "
                    f"(incluye múltiples como '(1) (1)').\n"
                    f"Ruta: '{file.parent}'"
                )


def validate_row_counts(
    dfs_capacity: list[pd.DataFrame],
    dfs_dispatch: list[pd.DataFrame],
) -> None:
    """Valida que cada par de archivos Excel tenga el mismo número de registros."""

    for df_capacity, df_dispatch in zip(dfs_capacity, dfs_dispatch):  # noqa
        rows_df_capacity = len(df_capacity)
        rows_df_dispatch = len(df_dispatch)

        if rows_df_capacity != rows_df_dispatch:
            df_capacity_path: Path = df_capacity.attrs["file_path"]
            df_dispatch_path: Path = df_dispatch.attrs["file_path"]
            df_capacity_filename = df_capacity_path.name
            df_dispatch_filename = df_dispatch_path.name

            raise ValueError(
                f"Validación fallida: inconsistencia en el número de registros detectada.\n"
                f"Archivo A: '{df_capacity_filename}' → {rows_df_capacity} filas\n"
                f"Archivo B: '{df_dispatch_filename}' → {rows_df_dispatch} filas\n"
                f"Ruta A: '{df_capacity_path}'\n"
                f"Ruta B: '{df_dispatch_path}'"
            )

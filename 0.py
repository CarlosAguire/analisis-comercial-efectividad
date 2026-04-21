from pathlib import Path

import pandas as pd

from src.config.parameters import (
    COLUMN_ORDER,
    COMERCIAL_EFFICACY_ANALYSIS,
    PROJECT_ROOT,
)

EFFICACY_ANALYSIS_FILE_PATH = PROJECT_ROOT / "datos-efectividad-comercial-IA.xlsx"


def reorder_columns(df: pd.DataFrame, order: list[str]) -> pd.DataFrame:

    return df.loc[:, order]


def read_xlsx_file(
    path: Path,
    sheet: int | str,
) -> pd.DataFrame:
    """
    Lee una hoja de Excel.
    - No se recortan espacios.
    - No se cambian mayúsculas/minúsculas.
    - No se normalizan caracteres.
    """

    return pd.read_excel(
        io=path,
        sheet_name=sheet,
        engine="openpyxl",
    )


def create_file(
    df: pd.DataFrame,
    path: Path,
    datetime_format: str | None = None,
) -> None:
    # 1. Dimensiones del DataFrame
    num_rows, num_columns = df.shape

    # Lista de nombres de columnas para los encabezados de la tabla
    columns = [{"header": col} for col in df.columns]

    with pd.ExcelWriter(
        path=path,
        engine="xlsxwriter",
        datetime_format=datetime_format,
    ) as writer:
        sheet_name = "DATOS"

        # 2. Volcamos los datos empezando en la fila 1 (dejamos la 0 para el encabezado)
        df.to_excel(
            excel_writer=writer,
            sheet_name=sheet_name,
            index=False,
            header=False,
            startrow=1,
        )

        # 3. Accedemos a los objetos internos de XlsxWriter
        worksheet = writer.sheets[sheet_name]

        # 4. Creamos la tabla sobre el rango de datos
        worksheet.add_table(
            0,
            0,
            num_rows,
            num_columns - 1,
            {
                "name": "Datos",
                "columns": columns,
                "style": None,
            },
        )


def main():
    df = read_xlsx_file(path=EFFICACY_ANALYSIS_FILE_PATH, sheet=0)
    df = reorder_columns(
        df=df,
        order=COLUMN_ORDER[COMERCIAL_EFFICACY_ANALYSIS],
    )
    create_file(
        df=df,
        path=PROJECT_ROOT / "datos-efectividad-comercial-IA-reordenado.xlsx",
    )


if __name__ == "__main__":
    main()

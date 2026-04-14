import re

import pandas as pd


class CleanDataFrame:
    @staticmethod
    def drop_columns(df: pd.DataFrame, columns_preserve: list[str]) -> pd.DataFrame:
        """Devuelve un `DataFrame` con solo las columnas a preservar."""

        return df.drop(columns=df.columns.difference(columns_preserve))

    @staticmethod
    def drop_duplicate_columns(
        df: pd.DataFrame,
        target_column: str,
        *,
        treat_empty_strings: bool = True,
        consider_empty_spaces: bool = True,
        inplace: bool = False,
    ) -> pd.DataFrame:

        if not inplace:
            df = df.copy()

        pattern = re.compile(rf"^{re.escape(target_column)}(?:\.(\d+))?$")
        family = [c for c in df.columns if pattern.fullmatch(c)]

        if not family:
            return df

        def __column_is_empty(serie: pd.Series) -> bool:
            s = serie

            if treat_empty_strings and s.dtype == "object":
                if consider_empty_spaces:
                    s = s.replace(r"^\s*$", pd.NA, regex=True)
                else:
                    s = s.replace("", pd.NA)

            return not s.notna().any()

        # 1) Identificar vacías y no vacías.
        empty_columns = [c for c in family if __column_is_empty(serie=df[c])]
        not_empty_columns = [c for c in family if c not in empty_columns]

        # 2) Eliminar columnas vacías.
        if empty_columns:
            df.drop(columns=empty_columns, inplace=True)

        # 3) Si la columna restante en su nombre tiene sufijo, renombrar al base.
        if len(not_empty_columns) == 1:
            remaining_column = not_empty_columns[0]

            if remaining_column != target_column:
                if target_column not in df.columns:
                    df.rename(columns={remaining_column: target_column}, inplace=True)
                else:
                    # Por seguridad, evitamos sobreescribir una columna existente.
                    pass

        return df

    @staticmethod
    def drop_duplicate_rows_by_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
        """
        Elimina filas duplicadas basándose en una única columna, conservando la primera
        aparición.
        """

        return df.drop_duplicates(subset=[column], keep="first").reset_index(drop=True)

    @staticmethod
    def filter(
        df: pd.DataFrame,
        include: dict[str, None | str | list[str]] | None = None,
        exclude: dict[str, None | str | list[str]] | None = None,
    ) -> pd.DataFrame:
        """
        Motor de filtrado avanzado que soporta tanto inclusión como exclusión dinámica.
        """

        # Inicializamos diccionarios vacíos si no se envían
        inclusion_filters = include or {}
        exclusion_filters = exclude or {}

        conditions = []

        # 1. Procesar Inclusiones (Lo que queremos ver)
        for column, value in inclusion_filters.items():
            if value is not None and column in df.columns:
                if isinstance(value, list):
                    conditions.append(f"`{column}` in @inclusion_filters['{column}']")
                else:
                    conditions.append(f"`{column}` == @inclusion_filters['{column}']")

        # 2. Procesar Exclusiones (Lo que queremos ocultar)
        for column, value in exclusion_filters.items():
            if value is not None and column in df.columns:
                if isinstance(value, list):
                    # La magia aquí es el 'not in'
                    conditions.append(
                        f"`{column}` not in @exclusion_filters['{column}']"
                    )
                else:
                    # Y aquí el '!='
                    conditions.append(f"`{column}` != @exclusion_filters['{column}']")

        # 3. Si no hubo condiciones válidas, retornamos el DF original
        if not conditions:
            return df

        # 4. Ensamblaje y ejecución
        query = " and ".join(conditions)

        return df.query(expr=query)

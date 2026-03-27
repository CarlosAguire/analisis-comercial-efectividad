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
    def filter(df: pd.DataFrame, filters: dict[str, str | list[str]]) -> pd.DataFrame:
        """
        Filtra un `DataFrame` usando filtros dinámicos, devuelve solo las filas que
        cumplen todos los filtros.
        """

        if not filters:
            return df

        mask = pd.Series(True, index=df.index)

        for field, value in filters.items():
            # Si la columna no existe, simplemente la ignoramos
            if field not in df.columns:
                continue

            # Si es lista o conjunto de filtros
            if isinstance(value, (list, set, tuple)):
                mask &= df[field].isin(value)
                continue

            # Si es un valor único
            else:
                mask &= df[field] == value

        return df[mask]

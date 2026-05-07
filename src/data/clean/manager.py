import re
from collections.abc import Iterable
from typing import Any, Literal

import pandas as pd


class CleanDataFrame:
    @staticmethod
    def drop_columns(df: pd.DataFrame, columns_preserve: list[str]) -> pd.DataFrame:
        """Devuelve un `DataFrame` con solo las columnas a preservar."""

        return df.drop(columns=df.columns.difference(columns_preserve), errors="ignore")

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
        filters: dict[str, dict[str, str | list[str]]],
        combine: Literal["and", "or"] = "and",
    ) -> pd.DataFrame:
        """
        Filtra un DataFrame con soporte para combinación AND / OR.

        combine:
            - "and": todas las condiciones deben cumplirse
            - "or": al menos una condición debe cumplirse
        """

        if not filters:
            return df

        final_mask = None

        def __is_iterable(value: Any) -> bool:

            return isinstance(value, Iterable) and not isinstance(value, str)

        def __combine_masks(mask1: Any, mask2: Any) -> Any:

            if mask1 is None:
                return mask2

            return mask1 & mask2 if combine == "and" else mask1 | mask2

        # ---------- INCLUDE ----------
        for field, value in filters.get("include", {}).items():
            if field not in df.columns:
                continue

            if __is_iterable(value=value):
                mask = df[field].isin(value)
            else:
                mask = df[field] == value

            final_mask = __combine_masks(mask1=final_mask, mask2=mask)

        # ---------- EXCLUDE ----------
        for field, value in filters.get("exclude", {}).items():
            if field not in df.columns:
                continue

            if __is_iterable(value=value):
                mask = ~df[field].isin(value)
            else:
                mask = df[field] != value

            final_mask = __combine_masks(mask1=final_mask, mask2=mask)

        # ---------- CONTAINS ----------
        for field, value in filters.get("contains", {}).items():
            if field not in df.columns:
                continue

            series = df[field].astype("string")

            if __is_iterable(value=value):
                mask = False
                for v in value:
                    mask |= series.str.contains(str(v), regex=False, na=False)
            else:
                mask = series.str.contains(str(value), regex=False, na=False)

            final_mask = __combine_masks(mask1=final_mask, mask2=mask)

        return df[final_mask] if final_mask is not None else df

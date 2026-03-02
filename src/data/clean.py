import re

import pandas as pd

from config import parameters


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

            # Si es un valor único
            else:
                mask &= df[field] == value

        return df[mask]


def clean_df_ofsc_dispatch(df: pd.DataFrame) -> pd.DataFrame:
    # Removemos columnas duplicadas que no necesitamos
    df_ofsc_dispatch = CleanDataFrame.drop_duplicate_columns(
        target_column="Notas de Cierre",
        df=df,
    )

    # Filtramos para eliminar filas que no necesitamos
    df_ofsc_dispatch = CleanDataFrame.filter(
        df=df_ofsc_dispatch,
        filters=parameters.OFSC_DISPATCH_FILTERS,  # type: ignore
    )

    # Removemos columnas que no necesitamos
    df_ofsc_dispatch = CleanDataFrame.drop_columns(
        columns_preserve=parameters.OFSC_DISPATCH_COLUMNS,
        df=df_ofsc_dispatch,
    )

    return df_ofsc_dispatch


def clean_df_ofsc_capacity(df: pd.DataFrame) -> pd.DataFrame:
    # Filtramos para eliminar filas que no necesitamos
    df_ofsc_capacity = CleanDataFrame.filter(
        filters=parameters.OFSC_CAPACITY_FILTERS,  # type: ignore
        df=df,
    )

    # 3. Removemos columnas que no necesitamos
    df_ofsc_capacity = CleanDataFrame.drop_columns(
        columns_preserve=parameters.OFSC_CAPACITY_COLUMNS,
        df=df_ofsc_capacity,
    )

    return df_ofsc_capacity


def clean_df_residential_plant(
    df: pd.DataFrame,
    df_ofsc_capacity: pd.DataFrame,
) -> pd.DataFrame:

    # Filtramos para eliminar filas que no necesitamos
    df_residential_plant = CleanDataFrame.filter(
        filters={"NOMBRE": df_ofsc_capacity["Asesor comercial"].tolist()},
        df=df,
    )

    # Removemos columnas que no necesitamos
    df_residential_plant = CleanDataFrame.drop_columns(
        columns_preserve=parameters.RESIDENTIAL_PLANT_COLUMNS,
        df=df_residential_plant,
    )

    # Removemos filas duplicadas que no necesitamos
    df_residential_plant = CleanDataFrame.drop_duplicate_rows_by_column(
        df=df_residential_plant,
        column="NOMBRE",
    )

    return df_residential_plant

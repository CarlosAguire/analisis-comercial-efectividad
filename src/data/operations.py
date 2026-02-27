from collections.abc import Iterable
from pathlib import Path

import numpy as np
import pandas as pd


def read_excel(path: Path, sheet: int | str) -> pd.DataFrame:
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


def drop_columns(df: pd.DataFrame, columns_preserve: list[str]) -> pd.DataFrame:
    """Devuelve un `DataFrame` con solo las columnas a preservar."""

    return df.drop(columns=df.columns.difference(columns_preserve))


def remove_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina columnas duplicadas en un `DataFrame`, manteniendo siempre las que contienen
    datos. Para cada grupo de columnas con el mismo nombre, se eliminan únicamente las
    duplicadas que estén completamente vacías. No se modifica el nombre ni el orden
    original de las columnas, solo se quitan las duplicadas vacías.
    """

    columns = df.columns
    duplicates = [column for column in columns if (columns == column).sum() > 1]

    # Máscara de columnas a conservar (por posición); comenzamos conservando todas
    keep_mask = np.ones(len(columns), dtype=bool)

    # Para cada nombre duplicado, revisa los índices de sus apariciones
    for column in set(duplicates):
        indices = [i for i, c in enumerate(columns) if c == column]

        # Mantiene la primera ocurrencia; evalúa las posteriores
        for idx in indices[1:]:
            # Si esta columna duplicada está totalmente vacía, se marca para eliminar
            if df.iloc[:, idx].isna().all():
                keep_mask[idx] = False

    return df.loc[:, keep_mask]


def drop_duplicates_by_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Elimina filas duplicadas basándose en una única columna, conservando la primera
    aparición.
    """

    return df.drop_duplicates(subset=[column], keep="first").reset_index(drop=True)


def join(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    foreign_key: str,
    columns_df1: Iterable[str] | None = None,
    columns_df2: Iterable[str] | None = None,
    normalize_spaces: bool = True,
    ignore_nulls_key: bool = True,
    verify_uniqueness: bool = True,
    verify_quantity: bool = True,
    verify_keys: bool = True,
    coercer_type: bool = True,
) -> pd.DataFrame:
    """
    Une DF1 y DF2 usando una `llave_foranea` tras validar que:
      - Tienen la misma cantidad de filas (opcional).
      - Tienen exactamente el mismo conjunto de llaves (opcional).
      - No hay duplicados en la llave (opcional).

    Luego devuelve un DataFrame unido por la llave.
    """

    # Copias ligeras (solo vista hasta que se modifican)
    df1 = (
        df1
        if columns_df1 is None
        else df1.loc[:, list(set([foreign_key]) | set(columns_df1))]
    )
    df2 = (
        df2
        if columns_df2 is None
        else df2.loc[:, list(set([foreign_key]) | set(columns_df2))]
    )

    # Validar existencia de la llave foranea
    missing = [
        n for n, df in (("DF1", df1), ("DF2", df2)) if foreign_key not in df.columns
    ]

    if missing:
        raise KeyError(
            f"La columna llave '{foreign_key}' no existe en: {', '.join(missing)}"
        )

    df1 = df1.copy()
    df2 = df2.copy()

    # Normalizar espacios si son cadenas de texto
    if normalize_spaces:
        if pd.api.types.is_string_dtype(df1[foreign_key]):
            df1[foreign_key] = df1[foreign_key].str.strip()
        if pd.api.types.is_string_dtype(df2[foreign_key]):
            df2[foreign_key] = df2[foreign_key].str.strip()

    # Alinear tipos de la llave foranea
    if coercer_type and df1[foreign_key].dtype != df2[foreign_key].dtype:
        try:
            df2[foreign_key] = df2[foreign_key].astype(df1[foreign_key].dtype)
        except Exception:
            # fallback seguro: string dtype
            df1[foreign_key] = df1[foreign_key].astype("string")
            df2[foreign_key] = df2[foreign_key].astype("string")

    # Manejo de nulos en la llave foranea
    if ignore_nulls_key:
        # Filtrar filas con llave no nula en cada DF (sin cruzar aún)
        df1 = df1[df1[foreign_key].notna()]
        df2 = df2[df2[foreign_key].notna()]
    else:
        # Si decides no ignorarlos, se mantiene la validación estricta
        nulls = []

        if df1[foreign_key].isna().any():
            nulls.append("DF1")
        if df2[foreign_key].isna().any():
            nulls.append("DF2")
        if nulls:
            raise ValueError(
                f"Existen valores nulos en la llave foranea '{foreign_key}' en: "
                f"{', '.join(nulls)}"
            )

    # Validaciones de cardinalidad y conjunto de llaves foraneas
    if verify_quantity and len(df1) != len(df2):
        raise ValueError(
            f"Los DataFrames tienen diferente número de filas: "
            f"DF1={len(df1):,}, DF2={len(df2):,}"
        )

    # Verificar que no hallan llaves foraneas duplicadas
    if verify_keys:
        keys1 = pd.Index(df1[foreign_key].unique())
        keys2 = pd.Index(df2[foreign_key].unique())
        missing_in_df2 = keys1.difference(keys2)
        missing_in_df1 = keys2.difference(keys1)

        if len(missing_in_df1) or len(missing_in_df2):
            detalles = []

            if len(missing_in_df2):
                detalles.append(
                    f"En DF1 y NO en DF2 (#{len(missing_in_df2)}). Ejemplos: "
                    f"{missing_in_df2[:10].tolist()}"
                )
            if len(missing_in_df1):
                detalles.append(
                    f"En DF2 y NO en DF1 (#{len(missing_in_df1)}). Ejemplos: "
                    f"{missing_in_df1[:10].tolist()}"
                )

            raise KeyError(
                f"Los conjuntos de llaves '{foreign_key}' no coinciden. "
                + " | ".join(detalles)
            )

    # Validar unicidad 1:1 para prevenir multiplicación de filas
    validate_arg = None

    if verify_uniqueness:
        dup1 = df1[foreign_key].duplicated(keep=False)
        dup2 = df2[foreign_key].duplicated(keep=False)

        if dup1.any() or dup2.any():
            examples1 = (
                df1.loc[dup1, foreign_key].value_counts().head(5).to_dict()
                if dup1.any()
                else {}
            )
            examples2 = (
                df2.loc[dup2, foreign_key].value_counts().head(5).to_dict()
                if dup2.any()
                else {}
            )

            raise ValueError(
                f"Se esperaba cardinalidad 1:1 en '{foreign_key}'. "
                "Duplicados DF1 (top 5): "
                f"{examples1} | Duplicados DF2 (top 5): {examples2}"
            )

        validate_arg = "one_to_one"

    # Union de los dos DF
    df = pd.merge(
        df1,
        df2,
        on=foreign_key,
        how="inner",
        sort=False,
        validate=validate_arg,
    )

    # Reordenar: llave primero
    columns = [foreign_key] + [c for c in df.columns if c != foreign_key]

    return df[columns]


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

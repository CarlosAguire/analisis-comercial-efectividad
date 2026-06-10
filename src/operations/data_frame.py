import re
import warnings
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Literal

import pandas as pd

from config import parameters


def read_xlsx_file(path: Path, sheet: int | str, dtype: dict[str, str]) -> pd.DataFrame:
    """
    Lee una hoja de Excel.
    - No se recortan espacios.
    - No se cambian mayúsculas/minúsculas.
    - No se normalizan caracteres.
    """

    warnings.filterwarnings(
        "ignore",
        category=UserWarning,
        message="Data Validation extension is not supported",
    )

    return pd.read_excel(
        io=path,
        sheet_name=sheet,
        engine="openpyxl",
        usecols=list(dtype.keys()),
        dtype=dtype,
    )


def read_xlsb_file(path: Path, sheet: int | str) -> pd.DataFrame:
    """
    Lee una hoja de Excel.
    - No se recortan espacios.
    - No se cambian mayúsculas/minúsculas.
    - No se normalizan caracteres.
    """

    return pd.read_excel(
        io=path,
        sheet_name=sheet,
        engine="calamine",
    )


def read_csv_file(path: Path, dtype: dict[str, str]) -> pd.DataFrame:
    """
    Lee una hoja de Excel.
    - No se recortan espacios.
    - No se cambian mayúsculas/minúsculas.
    - No se normalizan caracteres.
    """

    if path == parameters.RESIDENTIAL_PLANT_PATH:
        return pd.read_csv(
            filepath_or_buffer=path,
            engine="pyarrow",
            dtype_backend="pyarrow",
            usecols=list(dtype.keys()),
            dtype=dtype,  # type: ignore
            sep=";",
        )

    return pd.read_csv(
        filepath_or_buffer=path,
        encoding="latin1",
        low_memory=False,
    )


def reorder_columns(df: pd.DataFrame, order: list[str]) -> pd.DataFrame:

    return df.loc[:, order]


def normalize_dates(serie_fechas: pd.Series) -> pd.Series:

    # 1. Rescatar los números (ej: 45840 o 45840.0)
    fechas_numericas = pd.to_datetime(
        pd.to_numeric(serie_fechas, errors="coerce"), origin="1899-12-30", unit="D"
    )

    # 2. Rescatar los textos (ej: "02/07/2025") y fechas correctas
    fechas_texto = pd.to_datetime(
        serie_fechas,
        errors="coerce",
        dayfirst=True,  # Fundamental para fechas en formato DD/MM/YYYY
    )

    # 3. Combinar ambos mundos
    return fechas_numericas.fillna(fechas_texto)


def join(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    foreign_key: str,
    date_column: str | None = None,
    time_column: str | None = None,
    normalize_spaces: bool = True,
    ignore_nulls_key: bool = True,
    verify_uniqueness: bool = True,
    verify_quantity: bool = True,
    verify_keys: bool = True,
    coercer_type: bool = True,
) -> pd.DataFrame:
    """Une DF1 y DF2 garantizando una relación 1:1 mediante una LLAVE EFECTIVA

    construida progresivamente:

      1. foreign_key
      2. foreign_key + fecha (dd/mm/yyyy)
      3. foreign_key + fecha + hora (hh:mm AM/PM)

    La hora SOLO se usa si FK+Fecha sigue duplicada.
    Se asume que la fecha siempre viene en formato dd/mm/yyyy.
    """

    # ------------------------------------------------------------
    # Validaciones de existencia
    # ------------------------------------------------------------
    for name, df in (("DF1", df1), ("DF2", df2)):
        if foreign_key not in df.columns:
            raise KeyError(f"La columna llave '{foreign_key}' no existe en {name}")
        if date_column is not None and date_column not in df.columns:
            raise KeyError(f"La columna de fecha '{date_column}' no existe en {name}")

    df1 = df1.copy()
    df2 = df2.copy()

    # ------------------------------------------------------------
    # Normalizar espacios
    # ------------------------------------------------------------
    if normalize_spaces:
        for col in filter(None, [foreign_key, date_column, time_column]):
            if col in df1.columns and pd.api.types.is_string_dtype(df1[col]):
                df1[col] = df1[col].str.strip()
            if col in df2.columns and pd.api.types.is_string_dtype(df2[col]):
                df2[col] = df2[col].str.strip()

    # ------------------------------------------------------------
    # Alinear tipos de la FK
    # ------------------------------------------------------------
    if coercer_type and df1[foreign_key].dtype != df2[foreign_key].dtype:
        try:
            df2[foreign_key] = df2[foreign_key].astype(df1[foreign_key].dtype)
        except Exception:
            df1[foreign_key] = df1[foreign_key].astype("string")
            df2[foreign_key] = df2[foreign_key].astype("string")

    # ------------------------------------------------------------
    # Manejo de nulos en FK
    # ------------------------------------------------------------
    if ignore_nulls_key:
        df1 = df1[df1[foreign_key].notna()]
        df2 = df2[df2[foreign_key].notna()]
    else:
        if df1[foreign_key].isna().any() or df2[foreign_key].isna().any():
            raise ValueError(f"Existen valores nulos en la llave foránea '{foreign_key}'")

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------
    def __parse_date(s: pd.Series) -> pd.Series:
        # Si ya es datetime, lo dejamos pasar; si es string, forzamos dd/mm/yyyy
        if pd.api.types.is_datetime64_any_dtype(s):
            return s

        return pd.to_datetime(s, format="%d/%m/%Y", errors="coerce")

    def __parse_time_12h(s: pd.Series) -> pd.Series:
        s_clean = s.astype(str).str.upper()
        s_clean = s_clean.str.replace(".", "", regex=False)
        s_clean = s_clean.str.replace("A M", "AM", regex=False)
        s_clean = s_clean.str.replace("P M", "PM", regex=False)
        dt = pd.to_datetime(s_clean.str.strip(), format="%I:%M %p", errors="coerce")

        return dt.dt.strftime("%I:%M %p")

    # ------------------------------------------------------------
    # Construcción de llave efectiva
    # ------------------------------------------------------------
    df1["__join_key__"] = df1[foreign_key].astype("string")
    df2["__join_key__"] = df2[foreign_key].astype("string")

    dup1 = df1[foreign_key].duplicated(keep=False)
    dup2 = df2[foreign_key].duplicated(keep=False)
    any_dups_fk = dup1.any() or dup2.any()

    if any_dups_fk:
        if date_column is None:
            raise ValueError(
                "Se detectaron llaves foráneas duplicadas y no se proporcionó 'date_column'."
            )

        mask1 = dup1
        mask2 = dup2

        # Parseo directo usando estrictamente dd/mm/yyyy
        df1["_date_tmp_"] = __parse_date(df1[date_column])
        df2["_date_tmp_"] = __parse_date(df2[date_column])

        if df1.loc[mask1, "_date_tmp_"].isna().any():
            raise ValueError("Fechas inválidas en DF1 para llaves duplicadas")
        if df2.loc[mask2, "_date_tmp_"].isna().any():
            raise ValueError("Fechas inválidas en DF2 para llaves duplicadas")

        # Aseguramos un formato de texto homogéneo (con ceros a la izquierda) para la llave
        df1["_date_str_"] = df1["_date_tmp_"].dt.strftime("%d/%m/%Y")
        df2["_date_str_"] = df2["_date_tmp_"].dt.strftime("%d/%m/%Y")

        df1.loc[mask1, "__join_key__"] = (
            df1.loc[mask1, foreign_key].astype("string")
            + "||"
            + df1.loc[mask1, "_date_str_"]
        )
        df2.loc[mask2, "__join_key__"] = (
            df2.loc[mask2, foreign_key].astype("string")
            + "||"
            + df2.loc[mask2, "_date_str_"]
        )

        # 🔴 SEGUNDA CAPA: Hora si sigue duplicado
        dup1_after = df1["__join_key__"].duplicated(keep=False)
        dup2_after = df2["__join_key__"].duplicated(keep=False)

        if dup1_after.any() or dup2_after.any():
            if time_column is None:
                raise ValueError(
                    "Existen órdenes duplicadas incluso usando fecha. "
                    "Se requiere 'time_column' para garantizar unicidad."
                )

            df1["_time_str_"] = __parse_time_12h(df1[time_column])
            df2["_time_str_"] = __parse_time_12h(df2[time_column])

            if df1.loc[dup1_after, "_time_str_"].isna().any():
                raise ValueError("Horas inválidas en DF1 para órdenes duplicadas.")

            if df2.loc[dup2_after, "_time_str_"].isna().any():
                raise ValueError("Horas inválidas en DF2 para órdenes duplicadas.")

            df1.loc[dup1_after, "__join_key__"] = (
                df1.loc[dup1_after, "__join_key__"]
                + "||"
                + df1.loc[dup1_after, "_time_str_"]
            )
            df2.loc[dup2_after, "__join_key__"] = (
                df2.loc[dup2_after, "__join_key__"]
                + "||"
                + df2.loc[dup2_after, "_time_str_"]
            )

        # Limpieza de columnas temporales
        df1.drop(
            columns=[
                c for c in df1.columns if c.startswith("_date_") or c.startswith("_time_")
            ],
            inplace=True,
        )
        df2.drop(
            columns=[
                c for c in df2.columns if c.startswith("_date_") or c.startswith("_time_")
            ],
            inplace=True,
        )

    # ------------------------------------------------------------
    # Validaciones finales
    # ------------------------------------------------------------
    if verify_quantity and len(df1) != len(df2):
        df1_path: Path = df1.attrs.get("file_path", Path("Archivo_A"))
        df2_path: Path = df2.attrs.get("file_path", Path("Archivo_B"))

        raise ValueError(
            "Validación fallida: inconsistencia en el número de registros detectada.\n"
            f"Archivo A: {df1_path.name} → {len(df1)} filas\n"
            f"Archivo B: {df2_path.name} → {len(df2)} filas\n"
            f"Ruta A: {df1_path.parent}\n"
            f"Ruta B: {df2_path.parent}"
        )

    if verify_keys:
        k1 = set(df1["__join_key__"])
        k2 = set(df2["__join_key__"])

        if k1 != k2:
            only_df1 = k1 - k2
            only_df2 = k2 - k1
            if only_df1:
                print("Muestra en DF1 no encontrada en DF2:")
                print(df1[df1["__join_key__"] == next(iter(only_df1))])
            if only_df2:
                print("Muestra en DF2 no encontrada en DF1:")
                print(df2[df2["__join_key__"] == next(iter(only_df2))])

            raise ValueError(
                "Validación fallida: Los conjuntos de llaves efectivas no coinciden.\n"
                f"Archivo A: {df1.get('Ruta del Archivo', pd.Series(['Desconocido'])).iloc[0]}\n"  # noqa
                f"Archivo B: {df2.get('Ruta del Archivo', pd.Series(['Desconocido'])).iloc[0]}"  # noqa
            )

    validate_arg = "one_to_one" if verify_uniqueness else None

    # ------------------------------------------------------------
    # Merge final
    # ------------------------------------------------------------
    drop_cols = [foreign_key]
    if date_column is not None:
        drop_cols.append(date_column)
    if time_column is not None:
        drop_cols.append(time_column)

    df = pd.merge(
        df1,
        df2.drop(columns=[c for c in drop_cols if c in df2.columns]),
        on="__join_key__",
        how="inner",
        validate=validate_arg,
    )

    df.drop(columns="__join_key__", inplace=True)
    cols = [foreign_key] + [c for c in df.columns if c != foreign_key]

    return df[cols]


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


def complete_data(
    df: pd.DataFrame,
    df_dictionary: pd.DataFrame,
    column: str,
    key_match: Literal["exact", "contains"] = "exact",
) -> pd.DataFrame:

    df_copy = df.copy()
    df_dictionary_copy = df_dictionary.copy()

    columns_to_complete = [
        c for c in df_dictionary_copy.columns if c != column and c in df_copy.columns
    ]

    if not columns_to_complete:
        return df_copy

    # -----------------------------
    # CASO 1: MATCH EXACTO (merge)
    # -----------------------------
    if key_match == "exact":
        merged = df_copy.merge(
            df_dictionary_copy[[column] + columns_to_complete],
            on=column,
            how="left",
            suffixes=("", "_dicc"),
        )

        for col in columns_to_complete:
            merged[col] = merged[col].fillna(merged[f"{col}_dicc"])

        return merged.drop(
            columns=[f"{c}_dicc" for c in columns_to_complete],
            errors="ignore",
        )

    # --------------------------------
    # CASO 2: MATCH POR CONTAINS
    # --------------------------------
    base_keys = df_copy[column].astype(str).str.lower().str.strip()

    for _, dicc_row in df_dictionary_copy.iterrows():
        dicc_val = dicc_row[column]

        if pd.isna(dicc_val):
            continue

        dicc_str = str(dicc_val).lower().strip()

        if not dicc_str or dicc_str in ("nan", "<na>"):
            continue

        mask = base_keys.apply(
            lambda x: (  # type: ignore
                isinstance(x, str) and x not in ("nan", "<na>", "") and (x in dicc_str)  # noqa
            )
        )

        if mask.any():
            for col in columns_to_complete:
                df_copy.loc[mask, col] = dicc_row[col]

    return df_copy


def normalize_date(df: pd.DataFrame, column: str, input_format: str) -> pd.DataFrame:
    """
    Normaliza una columna de fechas según el formato de entrada y devuelve el
    DataFrame con:
    - La columna `column` en formato `dd/mm/yyyy`.
    - Una nueva columna `Mes` con el nombre del mes.
    """

    df = df.copy()

    # Limpieza ligera si es texto
    if pd.api.types.is_string_dtype(df[column]):
        df[column] = df[column].str.strip()

    # Mapear a strptime
    fmt_map = {
        "dd/mm/yy": "%d/%m/%y",
        "mm/dd/yy": "%m/%d/%y",
        "dd/mm/yyyy": "%d/%m/%Y",
        "mm/dd/yyyy": "%m/%d/%Y",
    }
    key = (input_format or "").strip().lower()

    if key not in fmt_map:
        allowed = ", ".join(fmt_map.keys())

        raise ValueError(f"input_format inválido: '{input_format}'. Use uno de: {allowed}")

    in_fmt = fmt_map[key]

    # Parseo a datetime
    if pd.api.types.is_datetime64_any_dtype(df[column]):
        dates = pd.to_datetime(df[column], errors="coerce")
    else:
        dates = pd.to_datetime(df[column], format=in_fmt, errors="coerce")

    # Formateo estándar de salida dd/mm/yyyy (texto)
    df[column] = dates.dt.strftime("%d/%m/%Y")

    return df


def drop_columns(df: pd.DataFrame, columns_preserve: list[str]) -> pd.DataFrame:
    """Devuelve un `DataFrame` con solo las columnas a preservar."""

    return df.drop(columns=df.columns.difference(columns_preserve), errors="ignore")


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


def drop_duplicate_rows_by_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Elimina filas duplicadas basándose en una única columna, conservando la primera
    aparición.
    """

    return df.drop_duplicates(subset=[column], keep="first").reset_index(drop=True)


def filter_df(
    df: pd.DataFrame,
    filters: dict[str, dict[str, str | list[str]]],
    combine: Literal["and", "or"] = "and",
) -> pd.DataFrame:
    """
    Filtra un `DataFrame` con soporte para combinación AND / OR.
    - "and": todas las condiciones deben cumplirse
    - "or": al menos una condición debe cumplirse
    """

    final_mask = None

    def __is_iterable(value: Any) -> bool:

        return isinstance(value, Iterable) and not isinstance(value, str)

    def __combine_masks(mask1: Any, mask2: Any) -> Any:

        if mask1 is None:
            return mask2

        return mask1 & mask2 if combine == "and" else mask1 | mask2

    def __validate_column(field: str) -> None:

        if field not in df.columns:
            raise KeyError(f"Error crítico en filtro: La columna '{field}' no existe.")

    # ---------- INCLUDE ----------
    for field, value in filters.get("include", {}).items():
        __validate_column(field)

        if __is_iterable(value=value):  # noqa
            mask = df[field].isin(value)
        else:
            mask = df[field] == value

        final_mask = __combine_masks(mask1=final_mask, mask2=mask)

    # ---------- EXCLUDE ----------
    for field, value in filters.get("exclude", {}).items():
        __validate_column(field)

        if __is_iterable(value=value):  # noqa
            mask = ~df[field].isin(value)
        else:
            mask = df[field] != value

        final_mask = __combine_masks(mask1=final_mask, mask2=mask)

    # ---------- CONTAINS ----------
    for field, value in filters.get("contains", {}).items():
        __validate_column(field)

        series = df[field].astype("string")

        if __is_iterable(value=value):
            mask = False
            for v in value:
                mask |= series.str.contains(str(v), regex=False, na=False)
        else:
            mask = series.str.contains(str(value), regex=False, na=False)

        final_mask = __combine_masks(mask1=final_mask, mask2=mask)

    return df[final_mask]  # type: ignore

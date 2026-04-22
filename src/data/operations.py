import warnings
from collections.abc import Iterable
from pathlib import Path
from typing import Literal

import pandas as pd


def read_xlsx_file(path: Path, sheet: int | str) -> pd.DataFrame:
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
        engine="pyxlsb",
    )


def read_csv_file(path: Path) -> pd.DataFrame:
    """
    Lee una hoja de Excel.
    - No se recortan espacios.
    - No se cambian mayúsculas/minúsculas.
    - No se normalizan caracteres.
    """

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
    Une DF1 y DF2 garantizando una relación 1:1 mediante una LLAVE EFECTIVA
    construida progresivamente:

      1. foreign_key
      2. foreign_key + fecha (dd/mm/yyyy)
      3. foreign_key + fecha + hora (hh:mm AM/PM)

    La hora SOLO se usa si FK+Fecha sigue duplicada.
    """

    # ------------------------------------------------------------
    # Subset de columnas
    # ------------------------------------------------------------
    cols1 = {foreign_key}
    cols2 = {foreign_key}

    if columns_df1 is not None:
        cols1 |= set(columns_df1)
    if columns_df2 is not None:
        cols2 |= set(columns_df2)

    if date_column is not None:
        cols1.add(date_column)
        cols2.add(date_column)

    if time_column is not None:
        cols1.add(time_column)
        cols2.add(time_column)

    df1 = (
        df1
        if (columns_df1 is None and date_column is None and time_column is None)
        else df1.loc[:, list(cols1)]
    )
    df2 = (
        df2
        if (columns_df2 is None and date_column is None and time_column is None)
        else df2.loc[:, list(cols2)]
    )

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
            raise ValueError(
                f"Existen valores nulos en la llave foránea '{foreign_key}'"
            )

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------
    def __infer_dayfirst_by_12_rule(s: pd.Series) -> bool | None:
        if pd.api.types.is_datetime64_any_dtype(s):
            return True

        parts = s.dropna().astype(str).str.split("/", expand=True)
        if parts.shape[1] != 3 or parts.empty:
            return None

        a = pd.to_numeric(parts[0], errors="coerce")
        b = pd.to_numeric(parts[1], errors="coerce")

        if (a > 12).any() and not (b > 12).any():
            return True
        if (b > 12).any() and not (a > 12).any():
            return False
        return None

    def __parse_date(s: pd.Series, dayfirst: bool) -> pd.Series:
        fmt = "%d/%m/%Y" if dayfirst else "%m/%d/%Y"
        return pd.to_datetime(s, format=fmt, errors="coerce")

    def __parse_time_12h(s: pd.Series) -> pd.Series:
        dt = pd.to_datetime(
            s.astype(str).str.strip(),
            format="%I:%M %p",
            errors="coerce",
        )
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
                "Se detectaron llaves foráneas duplicadas y no se proporcionó"
                " 'date_column'."
            )

        mask1 = dup1
        mask2 = dup2

        df1_dayfirst = __infer_dayfirst_by_12_rule(df1.loc[mask1, date_column])
        df2_dayfirst = __infer_dayfirst_by_12_rule(df2.loc[mask2, date_column])

        if df1_dayfirst is None:
            df1_dayfirst = True
        if df2_dayfirst is None:
            df2_dayfirst = False

        df1["_date_tmp_"] = __parse_date(df1[date_column], df1_dayfirst)
        df2["_date_tmp_"] = __parse_date(df2[date_column], df2_dayfirst)

        if df1.loc[mask1, "_date_tmp_"].isna().any():
            raise ValueError("Fechas inválidas en DF1 para llaves duplicadas")
        if df2.loc[mask2, "_date_tmp_"].isna().any():
            raise ValueError("Fechas inválidas en DF2 para llaves duplicadas")

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
                raise ValueError("Horas inválidas en DF1 para órdenes duplicadas")
            if df2.loc[dup2_after, "_time_str_"].isna().any():
                raise ValueError("Horas inválidas en DF2 para órdenes duplicadas")

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

        df1.drop(
            columns=[
                c
                for c in df1.columns
                if c.startswith("_date_") or c.startswith("_time_")
            ],
            inplace=True,
        )
        df2.drop(
            columns=[
                c
                for c in df2.columns
                if c.startswith("_date_") or c.startswith("_time_")
            ],
            inplace=True,
        )

    # ------------------------------------------------------------
    # Validaciones finales
    # ------------------------------------------------------------
    if verify_quantity and len(df1) != len(df2):
        raise ValueError(
            f"DF1 y DF2 tienen diferente número de filas ({len(df1)} vs {len(df2)})"
        )

    if verify_keys:
        k1 = set(df1["__join_key__"])
        k2 = set(df2["__join_key__"])
        if k1 != k2:
            raise KeyError(
                "Los conjuntos de llaves efectivas no coinciden entre DF1 y DF2"
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

        raise ValueError(
            f"input_format inválido: '{input_format}'. Use uno de: {allowed}"
        )

    in_fmt = fmt_map[key]

    # Parseo a datetime
    if pd.api.types.is_datetime64_any_dtype(df[column]):
        dates = pd.to_datetime(df[column], errors="coerce")
    else:
        dates = pd.to_datetime(df[column], format=in_fmt, errors="coerce")

    # Formateo estándar de salida dd/mm/yyyy (texto)
    df[column] = dates.dt.strftime("%d/%m/%Y")

    return df

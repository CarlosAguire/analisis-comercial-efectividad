from collections.abc import Iterable
from pathlib import Path

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


def join(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    foreign_key: str,
    date_column: str | None = None,
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
    Une DF1 y DF2 usando `foreign_key`. Si la llave se repite en alguno, se
    desambigua con `date_col` (normalizada a dd/mm/yy). Esta versión detecta
    automáticamente si las fechas de cada DF vienen en 'dd/mm/yy' o 'mm/dd/yy'
    (siempre consistentes por DF) y arma una llave efectiva:

      - Sin duplicados:   __join_key__ = foreign_key
      - Con duplicados:   __join_key__ = f"{foreign_key}||{fecha_dd/mm/yy}"

    Las validaciones siguen igual pero aplicadas sobre la llave efectiva:
      - Misma cantidad (opcional).
      - Mismo conjunto de llaves (opcional).
      - Unicidad 1:1 (opcional).
    """

    # --- Subset de columnas (incluir date_col si fue provista) ---
    cols1 = set([foreign_key])
    cols2 = set([foreign_key])
    if columns_df1 is not None:
        cols1 |= set(columns_df1)
    if columns_df2 is not None:
        cols2 |= set(columns_df2)
    if date_column is not None:
        cols1.add(date_column)
        cols2.add(date_column)

    df1 = (
        df1
        if (columns_df1 is None and date_column is None)
        else df1.loc[:, list(cols1)]
    )
    df2 = (
        df2
        if (columns_df2 is None and date_column is None)
        else df2.loc[:, list(cols2)]
    )

    # Validar existencia de columnas clave
    missing = [
        n for n, df in (("DF1", df1), ("DF2", df2)) if foreign_key not in df.columns
    ]
    if missing:
        raise KeyError(
            f"La columna llave '{foreign_key}' no existe en: {', '.join(missing)}"
        )

    if date_column is not None:
        missing_date = [
            n for n, df in (("DF1", df1), ("DF2", df2)) if date_column not in df.columns
        ]

        if missing_date:
            raise KeyError(
                f"La columna de fecha '{date_column}' no existe en: "
                f"{', '.join(missing_date)}"
            )

    df1 = df1.copy()
    df2 = df2.copy()

    # Normalizar espacios
    if normalize_spaces:
        if pd.api.types.is_string_dtype(df1[foreign_key]):
            df1[foreign_key] = df1[foreign_key].str.strip()
        if pd.api.types.is_string_dtype(df2[foreign_key]):
            df2[foreign_key] = df2[foreign_key].str.strip()
        if date_column is not None:
            if pd.api.types.is_string_dtype(df1[date_column]):
                df1[date_column] = df1[date_column].str.strip()
            if pd.api.types.is_string_dtype(df2[date_column]):
                df2[date_column] = df2[date_column].str.strip()

    # Alinear tipos de la llave foránea
    if coercer_type and df1[foreign_key].dtype != df2[foreign_key].dtype:
        try:
            df2[foreign_key] = df2[foreign_key].astype(df1[foreign_key].dtype)
        except Exception:
            df1[foreign_key] = df1[foreign_key].astype("string")
            df2[foreign_key] = df2[foreign_key].astype("string")

    # Manejo de nulos en la llave foránea
    if ignore_nulls_key:
        df1 = df1[df1[foreign_key].notna()]
        df2 = df2[df2[foreign_key].notna()]
    else:
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

    # Construcción de LLAVE EFECTIVA con normalización de fecha por DF
    dup1_fk = df1[foreign_key].duplicated(keep=False)
    dup2_fk = df2[foreign_key].duplicated(keep=False)
    any_dups_fk = dup1_fk.any() or dup2_fk.any()

    if any_dups_fk and date_column is None:
        raise ValueError(
            f"Se detectaron llaves foráneas repetidas en '{foreign_key}', "
            "pero no se proporcionó 'date_column'. Especifique la columna "
            "de fecha para desambiguar."
        )

    # Helper: inferir si la serie usa dayfirst (dd/mm/yy) por la regla >12
    def __infer_dayfirst_by_12_rule(s: pd.Series) -> bool | None:
        if pd.api.types.is_datetime64_any_dtype(s):
            return True

        # Esperamos "d{1,2}/d{1,2}/d{2}" (p.ej., '05/03/26')
        # Extraemos números para evaluar >12
        parts = s.dropna().astype(str).str.split("/", n=2, expand=True)

        if parts.shape[1] != 3 or parts.empty:
            return None

        try:
            a = pd.to_numeric(parts[0], errors="coerce")
            b = pd.to_numeric(parts[1], errors="coerce")
        except Exception:
            return None

        first_gt_12 = a > 12
        second_gt_12 = b > 12
        any_first = first_gt_12.any()
        any_second = second_gt_12.any()

        if any_first and not any_second:
            return True  # dd/mm/yy
        if any_second and not any_first:
            return False  # mm/dd/yy

        return None  # ambiguo (todos <=12 o mezcla inconsistente)

    # Helper: parsear según 'dayfirst' (si ya es datetime, lo respeta)
    def __parse_with_flag(s: pd.Series, dayfirst: bool) -> pd.Series:
        if pd.api.types.is_datetime64_any_dtype(s):
            return pd.to_datetime(s, errors="coerce")

        format = "%d/%m/%y" if dayfirst else "%m/%d/%y"

        return pd.to_datetime(s, format=format, dayfirst=dayfirst, errors="coerce")

    # Armar llave base
    df1["__join_key__"] = df1[foreign_key].astype("string")
    df2["__join_key__"] = df2[foreign_key].astype("string")

    # Si no hay duplicados, seguimos como antes
    if not any_dups_fk:
        pass
    else:
        # Conjunto de claves duplicadas (en cualquiera)
        dup_keys_union = pd.Index(df1.loc[dup1_fk, foreign_key].unique()).union(
            pd.Index(df2.loc[dup2_fk, foreign_key].unique())
        )
        mask1 = df1[foreign_key].isin(dup_keys_union)
        mask2 = df2[foreign_key].isin(dup_keys_union)

        # Inferir orientación por DF
        df1_dayfirst = __infer_dayfirst_by_12_rule(df1.loc[mask1, date_column])
        df2_dayfirst = __infer_dayfirst_by_12_rule(df2.loc[mask2, date_column])

        # Si alguna es ambigua, probamos combinaciones y elegimos la que hace coincidir
        if df1_dayfirst is None or df2_dayfirst is None:
            # Construir candidatos para df1
            df1_dt_d = __parse_with_flag(df1.loc[mask1, date_column], True)
            df1_dt_m = __parse_with_flag(df1.loc[mask1, date_column], False)
            df1_s_d = df1_dt_d.dt.strftime("%d/%m/%y")
            df1_s_m = df1_dt_m.dt.strftime("%d/%m/%y")

            # Construir candidatos para df2
            df2_dt_d = __parse_with_flag(df2.loc[mask2, date_column], True)
            df2_dt_m = __parse_with_flag(df2.loc[mask2, date_column], False)
            df2_s_d = df2_dt_d.dt.strftime("%d/%m/%y")
            df2_s_m = df2_dt_m.dt.strftime("%d/%m/%y")

            # Candidatos de llaves efectivas (solo en filas duplicadas)
            k1_d = (
                df1.loc[mask1, foreign_key].astype("string") + "||" + df1_s_d
            ).dropna()
            k1_m = (
                df1.loc[mask1, foreign_key].astype("string") + "||" + df1_s_m
            ).dropna()
            k2_d = (
                df2.loc[mask2, foreign_key].astype("string") + "||" + df2_s_d
            ).dropna()
            k2_m = (
                df2.loc[mask2, foreign_key].astype("string") + "||" + df2_s_m
            ).dropna()

            combos = {
                ("d", "d"): (set(k1_d.unique()), set(k2_d.unique())),
                ("d", "m"): (set(k1_d.unique()), set(k2_m.unique())),
                ("m", "d"): (set(k1_m.unique()), set(k2_d.unique())),
                ("m", "m"): (set(k1_m.unique()), set(k2_m.unique())),
            }
            valid = [
                cmb for cmb, (s1, s2) in combos.items() if s1 == s2 and len(s1) > 0
            ]

            if len(valid) == 1:
                df1_dayfirst = valid[0][0] == "d"
                df2_dayfirst = valid[0][1] == "d"
            elif len(valid) > 1:
                # Empate raro: preferimos (d, m) asumiendo DF opuestos
                if ("d", "m") in valid:
                    df1_dayfirst, df2_dayfirst = True, False
                elif ("m", "d") in valid:
                    df1_dayfirst, df2_dayfirst = False, True
                else:
                    # Último recurso: asumir df1=d, df2=m
                    df1_dayfirst, df2_dayfirst = True, False
            else:
                if df1_dayfirst is None:
                    df1_dayfirst = True
                if df2_dayfirst is None:
                    df2_dayfirst = False

        # Parsear definitivamente con las flags elegidas
        df1["_date_dt_tmp_"] = __parse_with_flag(df1[date_column], df1_dayfirst)
        df2["_date_dt_tmp_"] = __parse_with_flag(df2[date_column], df2_dayfirst)

        # Validar nulos en filas duplicadas
        if df1.loc[mask1, "_date_dt_tmp_"].isna().any():
            raise ValueError(
                f"Hay valores de fecha nulos/invalidos en '{date_column}' "
                "para llaves repetidas en DF1."
            )
        if df2.loc[mask2, "_date_dt_tmp_"].isna().any():
            raise ValueError(
                f"Hay valores de fecha nulos/invalidos en '{date_column}' "
                "para llaves repetidas en DF2."
            )

        # Normalizar a dd/mm/yy para construir la llave efectiva
        df1["_date_str_tmp_"] = df1["_date_dt_tmp_"].dt.strftime("%d/%m/%y")
        df2["_date_str_tmp_"] = df2["_date_dt_tmp_"].dt.strftime("%d/%m/%y")

        # En filas con fk duplicada, agregar fecha a la llave efectiva
        df1.loc[mask1, "__join_key__"] = (
            df1.loc[mask1, foreign_key].astype("string")
            + "||"
            + df1.loc[mask1, "_date_str_tmp_"]
        )
        df2.loc[mask2, "__join_key__"] = (
            df2.loc[mask2, foreign_key].astype("string")
            + "||"
            + df2.loc[mask2, "_date_str_tmp_"]
        )

        # Limpiar columnas temporales de fecha
        df1 = df1.drop(columns=["_date_dt_tmp_", "_date_str_tmp_"])
        df2 = df2.drop(columns=["_date_dt_tmp_", "_date_str_tmp_"])

    # Validación de cantidad (igual que antes)
    if verify_quantity and len(df1) != len(df2):
        raise ValueError(
            "Los DataFrames tienen diferente número de filas: "
            f"DF1={len(df1):,}, DF2={len(df2):,}"
        )

    # Verificación de conjuntos (ahora sobre la llave efectiva)
    if verify_keys:
        keys1 = pd.Index(df1["__join_key__"].unique())
        keys2 = pd.Index(df2["__join_key__"].unique())
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
                "Los conjuntos de llaves efectivas no coinciden. "
                + " | ".join(detalles)
            )

    # Unicidad 1:1 sobre la llave efectiva (igual que antes)
    validate_arg = None

    if verify_uniqueness:
        dup1 = df1["__join_key__"].duplicated(keep=False)
        dup2 = df2["__join_key__"].duplicated(keep=False)

        if dup1.any() or dup2.any():
            examples1 = (
                df1.loc[dup1, "__join_key__"].value_counts().head(5).to_dict()
                if dup1.any()
                else {}
            )
            examples2 = (
                df2.loc[dup2, "__join_key__"].value_counts().head(5).to_dict()
                if dup2.any()
                else {}
            )

            raise ValueError(
                "Se esperaba cardinalidad 1:1 en la llave efectiva. "
                f"Duplicados DF1 (top 5): {examples1} | Duplicados DF2 (top 5): "
                f"{examples2}"
            )

        validate_arg = "one_to_one"

    # Unión usando la llave efectiva
    drop_cols = [foreign_key]

    if date_column is not None and date_column in df2.columns:
        drop_cols.append(date_column)

    df2_no_fk = df2.drop(columns=drop_cols)
    df = pd.merge(
        df1,
        df2_no_fk,
        on="__join_key__",
        how="inner",
        sort=False,
        validate=validate_arg,
    )

    # Limpiar temporal y reordenar
    if "__join_key__" in df.columns:
        df = df.drop(columns=["__join_key__"])

    columns = [foreign_key] + [c for c in df.columns if c != foreign_key]

    return df[columns]


def create_file(df: pd.DataFrame, path: Path) -> None:
    with pd.ExcelWriter(path=path, engine="xlsxwriter", mode="w") as w:
        sheet_name = "DATOS"
        df.to_excel(excel_writer=w, index=False, sheet_name=sheet_name)

        worksheet = w.sheets[sheet_name]

        # Dimensiones del rango
        (n_rows, n_columns) = df.shape

        # Encabezados para la tabla
        columns = [{"header": col} for col in df.columns]

        # La creamos como tabla de Excel
        worksheet.add_table(
            0,
            0,
            n_rows,
            n_columns - 1,
            {"name": "TablaDatos", "columns": columns, "style": None},
        )


def join_by_sales_advisor(
    df: pd.DataFrame,
    df_dictionary: pd.DataFrame,
    *,
    sufijo_conflicto: str = "_dicc",
) -> pd.DataFrame:
    """
    Completa la información de `df_destino` tomando datos desde `df_diccionario`
    usando una columna en común (nombre).

    Parámetros
    ----------
    df_destino : DataFrame
        DataFrame que contiene la columna de nombres y necesita ser enriquecido.
    df_diccionario : DataFrame
        DataFrame maestro que contiene la información completa por persona.
        Se garantiza que `col_nombre` no tiene duplicados.
    col_nombre : str
        Nombre de la columna utilizada para emparejar en ambos DataFrames.
    columnas_a_traer : Iterable[str] | None
        Columnas que se traerán desde el diccionario (excepto la columna clave).
        Si None, se traen todas las columnas excepto la clave.
    sufijo_conflicto : str
        Sufijo que se agregará si existen nombres de columnas en conflicto.

    Retorna
    -------
    DataFrame enriquecido con las columnas traídas desde el diccionario.
    """

    # Copias para no alterar los originales
    df_copy = df.copy()
    df_dictionary_copy = df_dictionary.copy()

    # Determinar columnas a traer
    columns = [c for c in df_dictionary_copy.columns if c != "Asesor comercial"]

    # Generar DF reducido del diccionario
    df_dictionary_copy = df_dictionary_copy[["Asesor comercial"] + columns]

    return df_copy.merge(
        df_dictionary_copy,
        on="Asesor comercial",
        how="left",
        suffixes=("", sufijo_conflicto),
    )

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

# Regex ORIGINAL (con separadores): tres números con _ o - o espacio
DATE_RE = re.compile(r"(?<!\d)(\d{1,2})[ _-](\d{1,2})[ _-](\d{2,4})(?!\d)")


class AmbiguousDateError(Exception):
    pass


def __coerce_year(y: int) -> int:
    """Convierte año de 2 dígitos a 2000+YY. Ajusta aquí si necesitas otra regla."""
    if y < 100:
        return 2000 + y
    return y


def parse_date_from_name(
    filename: str,
    preferred_order: str | None = None,  # 'dmy' o 'mdy'
) -> date:
    """
    (Se deja tal cual tu implementación original para compatibilidad con otros usos.)
    """
    name = Path(filename).name
    m = DATE_RE.search(name)

    if not m:
        raise ValueError(f"No se encontró fecha en el nombre: {name}")

    a, b, y = m.groups()
    a, b, y = int(a), int(b), int(y)
    y = __coerce_year(y)

    a_gt_12 = a > 12
    b_gt_12 = b > 12

    if preferred_order is None:
        if a_gt_12 and not b_gt_12:
            d, m_ = a, b
        elif b_gt_12 and not a_gt_12:
            d, m_ = b, a
        elif a_gt_12 and b_gt_12:
            raise ValueError(f"Ambigüedad no resolvible (>12 en ambos): {name}")
        else:
            raise AmbiguousDateError(
                f"Fecha ambigua (ambas partes <=12) en: {name}. "
                f"Especifica preferred_order='dmy' o 'mdy'."
            )
    else:
        pref = preferred_order.lower()
        if pref not in ("dmy", "mdy"):
            raise ValueError("preferred_order debe ser 'dmy' o 'mdy'")
        if pref == "dmy":
            d, m_ = a, b
        else:  # 'mdy'
            d, m_ = b, a

    if not (1 <= m_ <= 12):
        raise ValueError(f"Mes inválido ({m_}) en: {name}")
    if not (1 <= d <= 31):
        raise ValueError(f"Día inválido ({d}) en: {name}")
    if y < 1900 or y > 2100:
        raise ValueError(f"Año fuera de rango razonable ({y}) en: {name}")

    return date(y, m_, d)


def normalize_without_date(filename: str) -> str:
    """Reemplaza el trozo de fecha por un token fijo para comparar nombres."""

    name = Path(filename).name

    return DATE_RE.sub("{DATE}", name)


@dataclass
class PairingResult:
    pairs: list[tuple[Path, Path]]
    only_in_dir1: list[Path]
    only_in_dir2: list[Path]
    ambiguous_in_dir1: list[Path]
    ambiguous_in_dir2: list[Path]
    errors: list[str]


def __extract_tokens(filename: str) -> tuple[int, int, int]:
    """
    Devuelve (a, b, y) tal como aparecen en el nombre, coaccionando el año.
    Solo valida el año; no decide si a es día o mes.
    """

    name = Path(filename).name
    m = DATE_RE.search(name)

    if not m:
        raise ValueError(f"No se encontró fecha en el nombre: {name}")

    a, b, y = map(int, m.groups())
    y = __coerce_year(y)

    if y < 1900 or y > 2100:
        raise ValueError(f"Año fuera de rango razonable ({y}) en: {name}")

    return a, b, y


def __is_impossible_date(a: int, b: int) -> bool:
    """Si a > 12 y b > 12, no puede ser fecha d/m válida en ningún orden."""

    return a > 12 and b > 12


def __is_ambiguous(a: int, b: int) -> bool:
    """Verdadero si tanto a como b son <= 12 (ambigüedad d/m)."""

    return a <= 12 and b <= 12


def __date_signature(a: int, b: int, y: int) -> tuple[int, int, int]:
    """Firma independiente del orden: (año, min(d,m), max(d,m))."""

    lo, hi = sorted((a, b))

    return (y, lo, hi)


def pair_files(dir1: Path, dir2: Path) -> PairingResult:

    d1 = Path(dir1)
    d2 = Path(dir2)

    if not d1.is_dir() or not d2.is_dir():
        raise NotADirectoryError("Alguna de las rutas no es carpeta.")

    files_dir1 = [p for p in d1.iterdir() if p.is_file()]
    files_dir2 = [p for p in d2.iterdir() if p.is_file()]

    # Índices por firma de fecha (y, min(a,b), max(a,b))
    idx1: dict[tuple[int, int, int], list[Path]] = {}
    idx2: dict[tuple[int, int, int], list[Path]] = {}

    ambiguous_in_dir1: list[Path] = []
    ambiguous_in_dir2: list[Path] = []
    errors: list[str] = []

    # Construir índices tolerantes al orden d/m
    for p in files_dir1:
        try:
            a, b, y = __extract_tokens(p.name)

            if __is_impossible_date(a, b):
                errors.append(
                    f"[dir1] {p.name}: ambos componentes >12; no es una fecha válida."
                )
                continue
            if __is_ambiguous(a, b):
                ambiguous_in_dir1.append(p)

            sig = __date_signature(a, b, y)
            idx1.setdefault(sig, []).append(p)
        except Exception as e:
            errors.append(f"[dir1] {p.name}: {e}")

    for p in files_dir2:
        try:
            a, b, y = __extract_tokens(p.name)

            if __is_impossible_date(a, b):
                errors.append(
                    f"[dir2] {p.name}: ambos componentes >12; no es una fecha válida."
                )
                continue
            if __is_ambiguous(a, b):
                ambiguous_in_dir2.append(p)

            sig = __date_signature(a, b, y)
            idx2.setdefault(sig, []).append(p)
        except Exception as e:
            errors.append(f"[dir2] {p.name}: {e}")

    # Validación: mismos nombres "sin fecha" en ambas carpetas
    if not files_dir1:
        errors.append(f"No se encontraron archivos dentro de dir1: {d1}")
    if not files_dir2:
        errors.append(f"No se encontraron archivos dentro de dir2: {d2}")

    norm1 = {normalize_without_date(p.name) for p in files_dir1}
    norm2 = {normalize_without_date(p.name) for p in files_dir2}

    if norm1 != norm2:
        only1 = norm1 - norm2
        only2 = norm2 - norm1

        if only1:
            errors.append(
                f"Nombres (sin fecha) presentes solo en dir1: {sorted(only1)}"
            )
        if only2:
            errors.append(
                f"Nombres (sin fecha) presentes solo en dir2: {sorted(only2)}"
            )

    # Emparejar por firma de fecha
    all_sigs = set(idx1.keys()) | set(idx2.keys())
    pairs: list[tuple[Path, Path]] = []
    only_in_dir1: list[Path] = []
    only_in_dir2: list[Path] = []

    def __sig_to_str(sig: tuple[int, int, int]) -> str:
        y, lo, hi = sig

        return f"{lo:02d}/{hi:02d}/{y} ~ {hi:02d}/{lo:02d}/{y}"

    for sig in sorted(all_sigs):
        files1 = idx1.get(sig, [])
        files2 = idx2.get(sig, [])

        if len(files1) == 1 and len(files2) == 1:
            pairs.append((files1[0], files2[0]))
        else:
            if not files2:
                only_in_dir1.extend(files1)
            if not files1:
                only_in_dir2.extend(files2)
            if len(files1) > 1 or len(files2) > 1:
                errors.append(
                    f"Hay {len(files1)} archivo(s) en dir1 y "
                    f"{len(files2)} en dir2 para la fecha {__sig_to_str(sig)}. "
                    "Se esperaba 1 y 1."
                )

    return PairingResult(
        pairs=pairs,
        only_in_dir1=only_in_dir1,
        only_in_dir2=only_in_dir2,
        ambiguous_in_dir1=ambiguous_in_dir1,
        ambiguous_in_dir2=ambiguous_in_dir2,
        errors=errors,
    )

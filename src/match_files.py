import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

# Busca un patrón de tres números (d/m/y o m/d/y) con separadores _ o -
DATE_RE = re.compile(r"(?<!\d)(\d{1,2})[ _-](\d{1,2})[ _-](\d{2,4})(?!\d)")


class AmbiguousDateError(Exception):
    pass


def _coerce_year(y: int) -> int:
    """Convierte año de 2 dígitos a 2000+YY. Ajusta aquí si necesitas otra regla."""

    if y < 100:
        return 2000 + y
    return y


def parse_date_from_name(
    filename: str,
    preferred_order: str | None = None,  # 'dmy' o 'mdy'
) -> date:
    """
    Extrae una fecha desde el nombre del archivo asumiendo un patrón numérico.
    - preferred_order: si 'dmy' la 1ª cifra es día; si 'mdy' la 1ª cifra es mes.
    - Si no se pasa y hay ambigüedad (ambas cifras <= 12), lanza AmbiguousDateError.
    """

    name = Path(filename).name
    m = DATE_RE.search(name)

    if not m:
        raise ValueError(f"No se encontró fecha en el nombre: {name}")

    a, b, y = m.groups()
    a, b, y = int(a), int(b), int(y)
    y = _coerce_year(y)

    # Si podemos desambiguar por rango (mes <= 12; día 1..31)
    a_gt_12 = a > 12
    b_gt_12 = b > 12

    if preferred_order is None:
        if a_gt_12 and not b_gt_12:
            # a es día (>=13..31) -> dmy
            d, m = a, b
        elif b_gt_12 and not a_gt_12:
            # b es día -> mdy
            d, m = b, a
        elif a_gt_12 and b_gt_12:
            # Ambos >12 no debería pasar con fechas reales
            raise ValueError(f"Ambigüedad no resolvible (>12 en ambos): {name}")
        else:
            # Ambos <= 12 => ambigua sin preferencia
            raise AmbiguousDateError(
                f"Fecha ambigua (ambas partes <=12) en: {name}. "
                f"Especifica preferred_order='dmy' o 'mdy'."
            )
    else:
        pref = preferred_order.lower()
        if pref not in ("dmy", "mdy"):
            raise ValueError("preferred_order debe ser 'dmy' o 'mdy'")
        if pref == "dmy":
            d, m = a, b
        else:  # 'mdy'
            d, m = b, a

    # Validaciones básicas
    if not (1 <= m <= 12):
        raise ValueError(f"Mes inválido ({m}) en: {name}")
    if not (1 <= d <= 31):
        raise ValueError(f"Día inválido ({d}) en: {name}")
    if y < 1900 or y > 2100:
        # Ajusta rangos si hace falta
        raise ValueError(f"Año fuera de rango razonable ({y}) en: {name}")

    return date(y, m, d)


def infer_order_for_folder(folder: Path, sample_limit: int = 100) -> str | None:
    """
    Intenta inferir el orden ('dmy' o 'mdy') para una carpeta.
    - Usa casos NO ambiguos (cuando uno de los dos primeros números > 12)
    - Si hay conflicto o insuficiencia de evidencia, devuelve None.
    """

    votes = {"dmy": 0, "mdy": 0}
    checked = 0

    for p in folder.iterdir():
        if not p.is_file():
            continue

        m = DATE_RE.search(p.name)

        if not m:
            continue

        a, b, _ = m.groups()
        a, b = int(a), int(b)

        a_gt_12 = a > 12
        b_gt_12 = b > 12

        if a_gt_12 and not b_gt_12:
            votes["dmy"] += 1
        elif b_gt_12 and not a_gt_12:
            votes["mdy"] += 1

        # si ambos <=12 o ambos >12 => no aporta evidencia
        checked += 1

        if checked >= sample_limit:
            break

    if votes["dmy"] > 0 and votes["mdy"] == 0:
        return "dmy"
    if votes["mdy"] > 0 and votes["dmy"] == 0:
        return "mdy"

    # Indeterminado o mixto
    return None


def normalize_without_date(filename: str) -> str:
    """
    Reemplaza el trozo de fecha (numérica) por un token fijo para comparar nombres
    independientemente del orden de la fecha.
    """

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


def pair_files(
    dir1: Path,
    dir2: Path,
    order1: str | None = None,
    order2: str | None = None,
) -> PairingResult:

    d1 = Path(dir1)
    d2 = Path(dir2)

    if not d1.is_dir() or not d2.is_dir():
        raise NotADirectoryError("Alguna de las rutas no es carpeta.")

    # Intento de inferencia automática si no se indicó orden
    ord1 = order1 or infer_order_for_folder(d1)
    ord2 = order2 or infer_order_for_folder(d2)

    # Índices por fecha
    idx1: dict[date, list[Path]] = {}
    idx2: dict[date, list[Path]] = {}

    ambiguous_in_dir1, ambiguous_in_dir2 = [], []
    errors = []

    # Construir índices
    for p in d1.iterdir():
        if not p.is_file():
            continue

        try:
            dt = parse_date_from_name(p.name, preferred_order=ord1)
            idx1.setdefault(dt, []).append(p)
        except AmbiguousDateError:
            ambiguous_in_dir1.append(p)
        except Exception as e:
            errors.append(f"[dir1] {p.name}: {e}")

    for p in d2.iterdir():
        if not p.is_file():
            continue

        try:
            dt = parse_date_from_name(p.name, preferred_order=ord2)
            idx2.setdefault(dt, []).append(p)
        except AmbiguousDateError:
            ambiguous_in_dir2.append(p)
        except Exception as e:
            errors.append(f"[dir2] {p.name}: {e}")

    # Validación 1: "Exactamente los mismos archivos" (independiente del orden de fecha)
    norm1 = {normalize_without_date(p.name) for p in d1.iterdir() if p.is_file()}
    norm2 = {normalize_without_date(p.name) for p in d2.iterdir() if p.is_file()}

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

    # Emparejar por fecha
    all_dates = set(idx1.keys()) | set(idx2.keys())
    pairs: list[tuple[Path, Path]] = []
    only_in_dir1: list[Path] = []
    only_in_dir2: list[Path] = []

    for dt in sorted(all_dates):
        files1 = idx1.get(dt, [])
        files2 = idx2.get(dt, [])

        # Si hay exactamente uno y uno, emparejamos directo
        if len(files1) == 1 and len(files2) == 1:
            pairs.append((files1[0], files2[0]))
        else:
            # Si alguno de los lados está vacío, los restantes quedan sin pareja
            if not files2:
                only_in_dir1.extend(files1)
            if not files1:
                only_in_dir2.extend(files2)
            # Si hay múltiples por fecha en alguno de los lados, reportamos
            if len(files1) > 1 or len(files2) > 1:
                errors.append(
                    f"Hay {len(files1)} archivo(s) en dir1 y {len(files2)} en dir2 "
                    f"para la fecha {dt.isoformat()}. Se esperaba 1 y 1."
                )
                # Sin lógica adicional para decidir emparejamiento en duplicados

    return PairingResult(
        pairs=pairs,
        only_in_dir1=only_in_dir1,
        only_in_dir2=only_in_dir2,
        ambiguous_in_dir1=ambiguous_in_dir1,
        ambiguous_in_dir2=ambiguous_in_dir2,
        errors=errors,
    )

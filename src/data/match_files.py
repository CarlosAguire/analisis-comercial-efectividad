import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

DATE_RE = re.compile(r"(?<!\d)(\d{1,2})[ _-](\d{1,2})[ _-](\d{2,4})(?!\d)")
COPY_SUFFIX_RE = re.compile(r"\s*\(\d+\)")


def normalize_without_date(filename: str) -> str:
    """Normaliza el nombre eliminando la fecha y sufijos de copia."""

    # 1. Reemplazamos la fecha por {DATE}
    norm = DATE_RE.sub("{DATE}", filename)

    # 2. Eliminamos los sufijos como " (1)", "(2)", etc.
    norm = COPY_SUFFIX_RE.sub("", norm)

    return norm


def coerce_year(y: int) -> int:
    """Convierte año de 2 dígitos a 2000 + YY."""

    return 2000 + y if y < 100 else y


def build_date(a: int, b: int, y: int, order: str) -> date:
    """
    Construye la fecha real según el orden indicado.
    order:
      - 'dmy' -> día / mes / año
      - 'mdy' -> mes / día / año
    """

    if order == "dmy":
        return date(y, b, a)
    elif order == "mdy":
        return date(y, a, b)
    else:
        raise ValueError("Formato invalido, use 'dmy' o 'mdy'")


def extract_date(filename: str, order: str) -> date:
    """Extrae y construye la fecha real a partir del nombre del archivo."""

    m = DATE_RE.search(filename)

    if not m:
        raise ValueError("No se encontró fecha en el nombre")

    a, b, y = map(int, m.groups())
    y = coerce_year(y)

    return build_date(a, b, y, order)


@dataclass
class PairingResult:
    pairs: list[tuple[Path, Path]]
    only_in_dir1: list[Path]
    only_in_dir2: list[Path]
    errors: list[str]


def pair_files(
    dir1: Path,
    dir2: Path,
    date_format_dir1: str = "dmy",
    date_format_dir2: str = "mdy",
) -> PairingResult:

    pairs = []
    only_in_dir1 = []
    only_in_dir2 = []
    errors = []

    index_dir2 = {}

    # Indexar archivos del dir2
    # Clave: (nombre_normalizado, fecha_real)
    for f in dir2.glob("*"):
        try:
            real_date = extract_date(filename=f.name, order=date_format_dir2)
            norm = normalize_without_date(filename=f.name)
            key = (norm, real_date)
            index_dir2.setdefault(key, []).append(f)

        except Exception as e:
            errors.append(f"{f}: {e}")

    # Procesar archivos del dir1
    for f in dir1.glob("*"):
        try:
            real_date = extract_date(filename=f.name, order=date_format_dir1)
            norm = normalize_without_date(filename=f.name)
            key = (norm, real_date)

            matches = index_dir2.get(key)

            if not matches:
                only_in_dir1.append(f)
            elif len(matches) == 1:
                pairs.append((f, matches[0]))
            else:
                errors.append(
                    f"Multiples coincidencias en dir2 para {f.name}: {matches}"
                )

        except Exception as e:
            errors.append(f"{f}: {e}")

    # Archivos en dir2 que nunca fueron usados
    used_dir2 = {p2 for _, p2 in pairs}

    for files in index_dir2.values():
        for f in files:
            if f not in used_dir2:
                only_in_dir2.append(f)

    return PairingResult(
        pairs=pairs,
        only_in_dir1=only_in_dir1,
        only_in_dir2=only_in_dir2,
        errors=errors,
    )

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

DATE_RE = re.compile(r"(?<!\d)(\d{1,2})[ _-](\d{1,2})[ _-](\d{2,4})(?!\d)")


def __normalize_without_date(filename: str) -> str:
    """Normaliza el nombre eliminando la fecha."""

    return DATE_RE.sub(repl="{DATE}", string=filename)


def __coerce_year(year: int) -> int:
    """Convierte año de 2 dígitos a 2000 + YY."""

    return 2000 + year if year < 100 else year


def __build_date(a: int, b: int, y: int, order: str) -> date:
    """
    Construye la fecha real según el orden indicado.
    - dmy -> día / mes / año
    - mdy -> mes / día / año
    """

    if order == "dmy":
        return date(year=y, month=b, day=a)
    elif order == "mdy":
        return date(year=y, month=a, day=b)
    else:
        raise ValueError("Formato invalido, use 'dmy' o 'mdy'")


def __extract_date(filename: str, order: str) -> date:
    """Extrae y construye la fecha real a partir del nombre del archivo."""

    m = DATE_RE.search(string=filename)

    if not m:
        raise ValueError("No se encontró fecha en el nombre")

    a, b, y = map(int, m.groups())
    y = __coerce_year(year=y)

    return __build_date(a=a, b=b, y=y, order=order)


@dataclass
class FileInventoryCatalog:
    """
    Catálogo estructurado que contiene el resultado del procesamiento de archivos.

    Esta clase actúa como un contenedor de datos de alto nivel para organizar los
    elementos analizados. Agrupa las relaciones uno a uno exitosas, los archivos
    huérfanos que se quedaron sin contraparte, y los inventarios cronológicos completos
    de todas las carpetas involucradas (incluyendo Fibra Óptica).
    """

    pairs_capacity_dispatch_folder: list[tuple[Path, Path]]
    unpaired_ftth_hfc_capacity_folder: list[Path]
    unpaired_ftth_hfc_dispatch_folder: list[Path]
    files_by_date_ftth_hfc_capacity_folder: list[tuple[date, Path]]
    files_by_date_ftth_hfc_dispatch_folder: list[tuple[date, Path]]
    files_by_date_fo_folder: list[tuple[date, Path]]


def process_file_folders(
    ftth_hfc_capacity_folder: Path,
    ftth_hfc_dispatch_folder: Path,
    fo_folder: Path,
    date_format_ftth_hfc_capacity_folder: str,
    date_format_ftth_hfc_dispatch_folder: str,
    date_format_fo_folder: str,
) -> FileInventoryCatalog:
    """
    Procesa múltiples directorios de red para catalogar, ordenar y emparejar sus
    archivos. Realiza un análisis integral sobre tres carpetas críticas del negocio:
    1. Establece un emparejamiento estricto uno a uno entre el área de Capacidad y
    Despacho basándose en sus nombres base normalizados y sus fechas lógicas internas.
    2. Aísla las anomalías identificando elementos huérfanos (sin pareja) en ambos
    directorios.
    3. Construye índices temporales cronológicos e independientes para las tres
    carpetas, permitiendo búsquedas dinámicas o filtros por rangos de fecha de manera
    eficiente.
    """

    index_ftth_hfc_dispatch_folder: dict[tuple[str, date], list[Path]] = {}
    unpaired_ftth_hfc_capacity_folder: list[Path] = []
    unpaired_ftth_hfc_dispatch_folder: list[Path] = []
    pairs_capacity_dispatch_folder: list[tuple[Path, Path]] = []

    # Listas para almacenar el historial cronológico
    files_by_date_ftth_hfc_capacity_folder: list[tuple[date, Path]] = []
    files_by_date_ftth_hfc_dispatch_folder: list[tuple[date, Path]] = []
    files_by_date_fo_folder: list[tuple[date, Path]] = []

    # Indexar archivos del ftth_hfc_dispatch_folder
    for f in ftth_hfc_dispatch_folder.glob("*"):
        if f.is_file() and f.suffix.lower() == ".txt":
            continue

        real_date = __extract_date(
            filename=f.name,
            order=date_format_ftth_hfc_dispatch_folder,
        )
        norm = __normalize_without_date(filename=f.name)
        key = (norm, real_date)
        index_ftth_hfc_dispatch_folder.setdefault(key, []).append(f)

        # Guardar en el inventario de fechas
        files_by_date_ftth_hfc_dispatch_folder.append((real_date, f))

    # Procesar archivos del ftth_hfc_capacity_folder
    for f in ftth_hfc_capacity_folder.glob("*"):
        if f.is_file() and f.suffix.lower() == ".txt":
            continue

        real_date = __extract_date(
            filename=f.name,
            order=date_format_ftth_hfc_capacity_folder,
        )
        norm = __normalize_without_date(filename=f.name)
        key = (norm, real_date)
        matches = index_ftth_hfc_dispatch_folder.get(key)

        # Guardar en el inventario de fechas
        files_by_date_ftth_hfc_capacity_folder.append((real_date, f))

        if not matches:
            unpaired_ftth_hfc_capacity_folder.append(f)
        elif len(matches) == 1:
            pairs_capacity_dispatch_folder.append((f, matches[0]))
        else:
            raise ValueError(
                f"Múltiples coincidencias en dir2 para {f.name}:{[m.name for m in matches]}"
            )

    # Procesar archivos de fo_folder (únicamente para inventario)
    for f in fo_folder.glob("*"):
        if f.is_file() and f.suffix.lower() == ".txt":
            continue

        real_date = __extract_date(
            filename=f.name,
            order=date_format_fo_folder,
        )
        files_by_date_fo_folder.append((real_date, f))

    # Archivos en ftth_hfc_dispatch_folder que nunca fueron usados
    used_ftth_hfc_dispatch_folder = {p2 for _, p2 in pairs_capacity_dispatch_folder}

    for files in index_ftth_hfc_dispatch_folder.values():
        for f in files:
            if f not in used_ftth_hfc_dispatch_folder:
                unpaired_ftth_hfc_dispatch_folder.append(f)

    # Ordenar los inventarios cronológicamente (de más antiguo a más reciente)
    files_by_date_ftth_hfc_capacity_folder.sort(key=lambda item: item[0])
    files_by_date_ftth_hfc_dispatch_folder.sort(key=lambda item: item[0])
    files_by_date_fo_folder.sort(key=lambda item: item[0])

    return FileInventoryCatalog(
        pairs_capacity_dispatch_folder=pairs_capacity_dispatch_folder,
        unpaired_ftth_hfc_capacity_folder=unpaired_ftth_hfc_capacity_folder,
        unpaired_ftth_hfc_dispatch_folder=unpaired_ftth_hfc_dispatch_folder,
        files_by_date_ftth_hfc_capacity_folder=files_by_date_ftth_hfc_capacity_folder,
        files_by_date_ftth_hfc_dispatch_folder=files_by_date_ftth_hfc_dispatch_folder,
        files_by_date_fo_folder=files_by_date_fo_folder,
    )


def get_latest_file(folder_path: Path) -> Path:
    """
    Obtiene el archivo más reciente dentro de una carpeta, basado en la fecha de
    última modificación.
    """

    # Obtenemos odos los archivos de la carpeta
    files = list(folder_path.iterdir())

    return max(files, key=lambda f: f.stat().st_mtime)


def filter_files_by_date(
    inventory: list[tuple[date, Path]],
    exact_date: date | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[Path]:
    """
    Filtra un inventario de archivos basándose en criterios de fecha.

    Permite buscar archivos que coincidan con una fecha exacta, o aquellos que
    caigan dentro de un rango de fechas especificado. Si solo se proporciona
    `start_date`, buscará desde esa fecha en adelante. Si solo se proporciona
    `end_date`, buscará hasta esa fecha inclusive.
    """

    if exact_date is not None:
        return [path for file_date, path in inventory if file_date == exact_date]

    return [
        path
        for file_date, path in inventory
        if (start_date is None or file_date >= start_date)
        and (end_date is None or file_date <= end_date)
    ]

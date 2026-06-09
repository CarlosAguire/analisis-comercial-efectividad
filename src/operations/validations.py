import re
from datetime import datetime
from pathlib import Path


def validate_xlsx(folder_path: Path) -> None:
    """
    Valida que todos los archivos dentro de una carpeta tengan extensión `.xlsx`.
    Recorre los archivos en la ruta proporcionada y lanza una excepción en el primer
    archivo que no cumpla con la condición.
    """

    for file in folder_path.iterdir():
        if file.is_file() and file.suffix.lower() not in [".xlsx", ".txt"]:
            raise ValueError(
                "Validación fallida: se encontró un archivo con extensión no permitida.\n"
                f"Archivo: '{file.name}'\n"
                f"Extensión detectada: '{file.suffix or 'sin extensión'}'\n"
                "Extensión esperada: '.xlsx'\n"
                f"Ruta: '{file.parent}'"
            )


def validate_csv(folder_path: Path) -> None:
    """
    Valida que todos los archivos dentro de una carpeta tengan extensión `.csv`.
    Recorre los archivos en la ruta proporcionada y lanza una excepción en el primer
    archivo que no cumpla con la condición.
    """

    for file in folder_path.iterdir():
        if file.is_file() and file.suffix.lower() not in [".csv", ".txt"]:
            raise ValueError(
                "Validación fallida: se encontró un archivo con extensión no permitida.\n"
                f"Archivo: '{file.name}'\n"
                f"Extensión detectada: '{file.suffix or 'sin extensión'}'\n"
                "Extensión esperada: '.csv'\n"
                f"Ruta: '{file.parent}'"
            )


def validate_duplicate_suffix(folder_path: Path) -> None:
    """
    Valida que ningún archivo dentro de una carpeta contenga sufijos de duplicado
    generados por Windows (por ejemplo: '(1)', '(2)', '(1) (1)', etc.) en su nombre.
    """

    # Detecta una o más ocurrencias de (n), incluso repetidas o separadas por espacios
    pattern = re.compile(r"(?:\(\d+\))+")

    for file in folder_path.iterdir():
        if file.is_file() and file.suffix.lower() == ".txt":
            continue
        if file.is_file() and not file.name.startswith("~$"):
            matches = pattern.findall(file.stem)

            if matches:
                raise ValueError(
                    "Validación fallida: se detectó un archivo con sufijo de duplicado.\n"
                    f"Archivo: '{file.name}'\n"
                    f"Nombre base: '{file.stem}'\n"
                    f"Sufijos detectados: {matches}\n"
                    "Regla incumplida: no se permiten sufijos tipo '(n)' en los nombres "
                    "(incluye múltiples como '(1) (1)').\n"
                    f"Ruta: '{file.parent}'"
                )


def validate_file_dates(folder_path: Path, date_format: str) -> bool:
    """
    Valida que todos los archivos de la carpeta terminen con una fecha válida según el
    formato especificado.
    """

    # Mapeo de los formatos solicitados a la nomenclatura de strptime
    valid_formats = {"dmy": "%d_%m_%y", "mdy": "%m_%d_%y"}

    if date_format not in valid_formats:
        raise ValueError(
            "Validación fallida: Parámetro de formato no soportado.\n"
            f"Carpeta evaluada: '{folder_path.resolve()}'\n"
            f"Formato recibido: '{date_format}'\n"
            "Formatos permitidos: 'dmy' o 'mdy'"
        )

    # Expresión regular para capturar el patrón _XX_XX_XX
    date_pattern = re.compile(r"_(\d{2}_\d{2}_\d{2})$")

    strptime_format = valid_formats[date_format]

    for file_path in folder_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() == ".txt":
            continue

        stem = file_path.stem
        match = date_pattern.search(stem)

        if not match:
            raise ValueError(
                "Validación fallida: El archivo no cumple con el formato de fecha.\n"
                f"Archivo problemático: '{file_path.name}'\n"
                f"Formato valido: '{date_format}'\n"
                f"Carpeta evaluada: '{folder_path.resolve()}'\n"
            )

        date_string = match.group(1)

        try:
            datetime.strptime(date_string, strptime_format)
        except ValueError:
            raise ValueError(  # noqa
                "Validación fallida: Fecha inválida.\n"
                f"Archivo problemático: '{file_path.name}'\n"
                f"Carpeta evaluada: '{folder_path.resolve()}'\n"
                f"Formato exigido: '{date_format}' ({strptime_format})\n"
            )

    return True


def validate_exact_file_path(path: Path) -> Path:
    """
    Valida que un archivo exista exactamente con el nombre y extensión proporcionados.
    Si no existe, determina si el fallo se debe a una extensión incorrecta o a la
    ausencia total del archivo en el directorio.
    """

    parent_dir = path.parent

    # El archivo existe exactamente como se solicitó
    if path.is_file():
        return path

    # Buscar coincidencias con el mismo nombre base (stem) pero cualquier extensión
    coincidences = list(parent_dir.glob(f"{path.stem}.*"))

    # Filtramos para asegurarnos de que sean archivos
    similar_files = [p.name for p in coincidences if p.is_file()]

    if similar_files:
        names_found = ", ".join(similar_files)

        raise ValueError(
            "Validación fallida: El archivo existe pero con una extensión diferente.\n"
            f"Archivo esperado: '{path.name}'\n"
            f"Alternativas encontradas: '{names_found}'\n"
            f"Carpeta evaluada: '{parent_dir.resolve()}'\n"
        )

    # El archivo definitivamente no existe
    raise FileNotFoundError(
        "Validación fallida: El archivo no existe en el directorio especificado.\n"
        f"Archivo esperado: '{path.name}'\n"
        f"Carpeta evaluada: '{parent_dir.resolve()}'\n"
    )

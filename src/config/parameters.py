from pathlib import Path

# Configuración de ruta raíz del proyecto
THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parent.parent.parent
UTILS_FOLDER = PROJECT_ROOT / "databases" / "utils"
DATABASES_FOLDER = PROJECT_ROOT / "databases"

# Configuración del modo de ejecución
DEBUG = True

# Lista de columnas a CONSERVAR de cada tabla
OFSC_DISPATCH_COLUMNS = ["Notas de Cierre", "Orden de trabajo", "Fecha"]
OFSC_DISPATCH_FILTERS = {
    "Estado": "No completado",
    "Tipo de Actividad": "Instalaciones",
    "Tipo de Red": "Pymes",
}
OFSC_CAPACITY_COLUMNS = [
    "Estado",
    "Razón",
    "Tipo de Actividad",
    "Ciudad",
    "Orden de trabajo",
    "Tipo de Red",
    "Asesor comercial",
    "Código Asesor comercial",
    "Fecha",
]
OFSC_CAPACITY_FILTERS = {
    "Estado": "No completado",
    "Tipo de Actividad": "Instalaciones",
    "Tipo de Red": "Pymes",
}
RESIDENTIAL_PLANT_COLUMNS = [
    "NOMBRE",
    "GV-Especialista",
    "JEFE 1 CANAL REGIONAL",
    "CANAL2",
]


# Archivo de salida
OUTPUT_FILE_PATH = PROJECT_ROOT / "data.xlsx"


# Salidas individuales de archivos de apoyo
UTILS_FOLDER.mkdir(parents=True, exist_ok=True)
CLEAN_OFSC_PATH = UTILS_FOLDER / "limpio_ofsc.xlsx"
CLEAN_OFSC_CAPACITY_PATH = UTILS_FOLDER / "limpio_ofsc_capacity.xlsx"
CLEAN_OFSC_DISPATCH_PATH = UTILS_FOLDER / "limpio_ofsc_dispatch.xlsx"
CLEAN_RESIDENTIAL_PLANT_PATH = UTILS_FOLDER / "limpio_planta_residencial.xlsx"

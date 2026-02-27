from pathlib import Path

# Configuración de ruta raíz del proyecto
THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parent.parent.parent

# Configuración del modo de ejecución
DEBUG = True

# Lista de columnas a CONSERVAR de cada tabla
OFSC_DISPATCH_COLUMNS = ["Notas de Cierre", "Orden de trabajo"]
OFSC_CAPACITY_COLUMNS = [
    "Estado",
    "Razón",
    "Tipo de Actividad",
    "Ciudad",
    "Orden de trabajo",
    "Tipo de Red",
    "Asesor comercial",
    "Código Asesor comercial",
]
RESIDENTIAL_PLANT_COLUMNS = [
    "NOMBRE",
    "GV-Especialista",
    "JEFE 1 CANAL REGIONAL",
    "CANAL2",
]


# Archivo de salida
OUTPUT_FILE_PATH = PROJECT_ROOT / "data.xlsx"


# Salidas individuales de archivos de apoyo
UTILS_FOLDER = PROJECT_ROOT / "databases" / "utils"
UTILS_FOLDER.mkdir(parents=True, exist_ok=True)
CLEAN_OFSC_PATH = UTILS_FOLDER / "limpio_ofsc.xlsx"
CLEAN_RESIDENTIAL_PLANT_PATH = UTILS_FOLDER / "limpio_planta_residencial.xlsx"

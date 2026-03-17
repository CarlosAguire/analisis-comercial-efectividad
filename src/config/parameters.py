from pathlib import Path

# Configuración de ruta raíz del proyecto
THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parent.parent.parent
UTILS_FOLDER = PROJECT_ROOT / "databases" / "utils"
DATABASES_FOLDER = PROJECT_ROOT / "databases"
LOGS_FOLDER = PROJECT_ROOT / "logs"

# Configuración del modo de ejecución
DEBUG = True

# Lista de columnas a CONSERVAR de cada tabla
OFSC_DISPATCH_COLUMNS = ["Notas de Cierre", "Orden de trabajo", "Fecha", "Compañia"]
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
RESIDENTIAL_PLANT_COLUMNS = [
    "NOMBRE",
    "GV-Especialista",
    "GV-Descripcion",
    "JEFE 1 CANAL REGIONAL",
    "CANAL2",
]


# Filtros de cada taqbla
OFSC_DISPATCH_FILTERS = {
    "Estado": "No completado",
    "Tipo de Actividad": "Instalaciones",
    "Tipo de Red": "Pymes",
}
OFSC_CAPACITY_FILTERS = {
    "Estado": "No completado",
    "Tipo de Actividad": "Instalaciones",
    "Tipo de Red": "Pymes",
}


# Diccionario para renombrar columnas en la tabla final
FINAL_COLUMNS = {
    "Orden de trabajo": "Orden de Trabajo",
    "Compañia": "Aliado",
    "Asesor comercial": "Asesor Comercial",
    "Código Asesor comercial": "Código del Asesor Comercial",
    "GV-Especialista": "Especialista",
    "GV-Descripcion": "Proveedor",
    "CANAL2": "Canal",
    "JEFE 1 CANAL REGIONAL": "Jefe de Canal",
}


# Archivo de salida
OUTPUT_FILE_PATH = PROJECT_ROOT / "datos.xlsx"


# Salidas individuales de archivos de apoyo
UTILS_FOLDER.mkdir(parents=True, exist_ok=True)
CLEAN_OFSC_PATH = UTILS_FOLDER / "limpio_ofsc.xlsx"
CLEAN_OFSC_CAPACITY_PATH = UTILS_FOLDER / "limpio_ofsc_capacity.xlsx"
CLEAN_OFSC_DISPATCH_PATH = UTILS_FOLDER / "limpio_ofsc_dispatch.xlsx"
CLEAN_RESIDENTIAL_PLANT_PATH = UTILS_FOLDER / "limpio_planta_residencial.xlsx"
LOGS_PATH = LOGS_FOLDER / "logs.txt"
PY_OUT_LOGS_PATH = LOGS_FOLDER / "py_out_logs.txt"

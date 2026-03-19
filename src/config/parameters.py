from pathlib import Path

# Configuración del modo de ejecución
DEBUG = True


# Configuración de ruta raíz del proyecto
THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parent.parent.parent


# Configuración de rutas para archivos de entrada y salida
UTILS_FOLDER = PROJECT_ROOT / "databases" / "utils"
DATABASES_FOLDER = PROJECT_ROOT / "databases"
LOGS_FOLDER = PROJECT_ROOT / "logs"
RESIDENTIAL_PLANT_PATH = DATABASES_FOLDER / "RM Planta Residencial.xlsx"
OFSC_CAPACITY_FOLDER = DATABASES_FOLDER / "OFSC" / "Area de Capacidades"
OFSC_DISPATCH_FOLDER = DATABASES_FOLDER / "OFSC" / "Area de Despacho"


# Tipos de análisis
COMERCIAL_EFFICACY_ANALYSIS = "análisis de efectividad comercial"
CONTACT_ANALYSIS = "análisis de contacto"


# Lista de columnas a CONSERVAR de cada tabla
COLUMNS_TO_RESERVE = {
    COMERCIAL_EFFICACY_ANALYSIS: {
        "ofsc_dispatch": [
            "Notas de Cierre",
            "Orden de trabajo",
            "Fecha",
            "Compañia",
        ],
        "ofsc_capacity": [
            "Estado",
            "Razón",
            "Tipo de Actividad",
            "Ciudad",
            "Orden de trabajo",
            "Tipo de Red",
            "Asesor comercial",
            "Código Asesor comercial",
            "Fecha",
        ],
        "residential_plant": [
            "NOMBRE",
            "GV-Especialista",
            "GV-Descripcion",
            "JEFE 1 CANAL REGIONAL",
            "CANAL2",
        ],
    },
    CONTACT_ANALYSIS: {
        "ofsc_capacity": [
            "Tipo de Actividad",
            "Ciudad",
            "Orden de trabajo",
            "Tipo de Red",
            "Compañia",
            "Asesor comercial",
            "Código Asesor comercial",
            "Teléfono",
            "Telefono dos del cliente",
            "Teléfono 3",
            "Celuar del contacto",
            "Fecha",
        ],
        "residential_plant": [
            "NOMBRE",
            "GV-Especialista",
            "GV-Descripcion",
            "JEFE 1 CANAL REGIONAL",
            "CANAL2",
        ],
    },
}


# Filtros para cada tipo de análisis
FILTERS = {
    COMERCIAL_EFFICACY_ANALYSIS: {
        "ofsc_dispatch": {
            "Estado": "No completado",
            "Tipo de Actividad": "Instalaciones",
            "Tipo de Red": "Pymes",
        },
        "ofsc_capacity": {
            "Estado": "No completado",
            "Tipo de Actividad": "Instalaciones",
            "Tipo de Red": "Pymes",
        },
    },
    CONTACT_ANALYSIS: {
        "ofsc_capacity": {
            "Tipo de Actividad": ["Instalaciones", "INSTALACIONES FTTH"],
            "Tipo de Red": ["Pymes", "FTTX"],
        },
    },
}


# Diccionario para renombrar columnas en la tabla final
FINAL_COLUMNS = {
    COMERCIAL_EFFICACY_ANALYSIS: {
        "Orden de trabajo": "Orden de Trabajo",
        "Compañia": "Aliado",
        "Asesor comercial": "Asesor Comercial",
        "Código Asesor comercial": "Código del Asesor Comercial",
        "GV-Especialista": "Especialista",
        "GV-Descripcion": "Proveedor",
        "CANAL2": "Canal",
        "JEFE 1 CANAL REGIONAL": "Jefe de Canal",
    },
    CONTACT_ANALYSIS: {
        "Orden de trabajo": "Orden de Trabajo",
        "Compañia": "Aliado",
        "Asesor comercial": "Asesor Comercial",
        "Código Asesor comercial": "Código del Asesor Comercial",
        "GV-Especialista": "Especialista",
        "GV-Descripcion": "Proveedor",
        "CANAL2": "Canal",
        "JEFE 1 CANAL REGIONAL": "Jefe de Canal",
    },
}

# Configuración de jefaturas por ciudad
HEADQUARTERS = {
    "BORRERO MELO TATIANA ESPERANZA": [
        "YOPAL",
        "VILLAVICENCIO",
        "VILLANUEVA",
        "VILLA DE SAN DIEGO DE UBA",
        "TUNJA",
        "SOGAMOSO",
        "RESTREPO",
        "PAIPA",
        "DUITAMA",
        "CUMARAL",
        "CHIQUINQUIRA",
        "BUCARAMANGA",
        "ARAUCA",
        "AGUAZUL",
        "ACACIAS",
    ],
    "CORREAL MEDINA CARLOS HUMBERTO": [
        "VILLA DEL ROSARIO",
        "VILLA CARO",
        "SAN GIL",
        "PIEDECUESTA",
        "PAMPLONA",
        "OCA#A",
        "LOS PATIOS",
        "GIRON",
        "FLORIDABLANCA",
        "CUCUTA",
        "BARRANCABERMEJA",
    ],
    "CUNDINAMARCA": [
        "VILLETA",
        "SILVANIA",
        "RICAURTE",
        "PACHO",
        "MONGUA",
        "LA MESA",
        "GUADUAS",
        "GIRARDOT",
        "FUSAGASUGA",
    ],
}


# Archivo de salida
EFFICACY_ANALYSIS_FILE_PATH = PROJECT_ROOT / "datos-efectividad-comercial.xlsx"
CONTACT_ANALYSIS_FILE_PATH = PROJECT_ROOT / "datos-analisis-contacto.xlsx"


# Salidas individuales de archivos de apoyo
UTILS_FOLDER.mkdir(parents=True, exist_ok=True)
CLEAN_OFSC_PATH = UTILS_FOLDER / "limpio_ofsc.xlsx"
CLEAN_OFSC_CAPACITY_PATH = UTILS_FOLDER / "limpio_ofsc_capacity.xlsx"
CLEAN_OFSC_DISPATCH_PATH = UTILS_FOLDER / "limpio_ofsc_dispatch.xlsx"
CLEAN_RESIDENTIAL_PLANT_PATH = UTILS_FOLDER / "limpio_planta_residencial.xlsx"
LOGS_PATH = LOGS_FOLDER / "logs.txt"
PY_OUT_LOGS_PATH = LOGS_FOLDER / "py_out_logs.txt"

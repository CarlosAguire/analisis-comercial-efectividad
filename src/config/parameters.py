from pathlib import Path

# Configuración del modo de ejecución
DEBUG = False


# Configuración de ruta raíz del proyecto
THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parent.parent.parent


# Configuración de rutas de carpetas
DATABASES_FOLDER = PROJECT_ROOT / "databases"
FTTH_HFC_TREE_FOLDER = DATABASES_FOLDER / "FTTH y HFC"
BACKLOG_FOLDER = DATABASES_FOLDER / "Back Transversal"
UTILS_FOLDER = PROJECT_ROOT / "databases" / "utils"
COMERCIAL_UTILS_FOLDER = UTILS_FOLDER / "comercial"
CONTACT_UTILS_FOLDER = UTILS_FOLDER / "contacto"
BACKLOG_UTILS_FOLDER = UTILS_FOLDER / "backlog"
PRODUCTIVITY_UTILS_FOLDER = UTILS_FOLDER / "productividad"
MIGRATIONS_UTILS_FOLDER = UTILS_FOLDER / "migraciones"
FO_TREE_FOLDER = DATABASES_FOLDER / "FO"
LOGS_FOLDER = PROJECT_ROOT / "logs"


# Configuración de rutas de archivos
RESIDENTIAL_PLANT_PATH = DATABASES_FOLDER / "RM Planta Residencial.xlsx"
BACKLOG_PATH = DATABASES_FOLDER / "Backlog_Nacional_Por_Produccion.csv"
GPON_BASES_PATH = DATABASES_FOLDER / "BASES CENTROS COMERCIALES GPON.xlsx"
BROWNFIELD_BASES_PATH = DATABASES_FOLDER / "BASE BROWNFIELD 2025 Oriente.xlsb"
PY_OUT_LOGS_PATH = LOGS_FOLDER / "py_out_logs.txt"
LOGS_PATH = LOGS_FOLDER / "logs.txt"


# Tipos de análisis
COMERCIAL_EFFICACY_ANALYSIS = "análisis de efectividad comercial"
CONTACT_ANALYSIS = "análisis de contacto"
BACKLOG_ANALYSIS = "análisis de backlog"
PRODUCTIVITY_ANALYSIS = "análisis de productividad"
MIGRATIONS_ANALYSIS = "análisis de migraciones"


# Lista de columnas a conservar
COLUMNS_TO_RESERVE = {
    COMERCIAL_EFFICACY_ANALYSIS: {
        "ofsc_dispatch": [
            "Notas de Cierre",
            "Orden de trabajo",
            "Fecha",
            "Inicio",
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
            "Inicio",
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
    BACKLOG_ANALYSIS: {
        "backlog": [
            "TIPO_TRABAJO",
            "TIPO_BACKLOG",
            "CUENTA",
            "OT/LL",
            "FECHA_CREADO",
            "CONVENIENCIA",
            "Comunidad",
            "Opera",
            "FECHA_AGENDA_FUTURO",
            "ESTADO_VISITA",
            "ANTIGUEDAD_ULTIMA_VISITA",
            "CUENTA_MATRIZ",
            "NOMBRE",
            "GV-Especialista",
            "GV-Descripcion",
            "CANAL2",
            "Alerta",
        ],
        "residential_plant": [
            "NOMBRE",
            "GV-Especialista",
            "GV-Descripcion",
            "JEFE 1 CANAL REGIONAL",
            "CANAL2",
        ],
    },
    MIGRATIONS_ANALYSIS: {
        "brownfield_bases": [
            "ESTADO REGIONAL",
            "DESMONTE DE NODOS 1",
            "TIPIFICACION",
            "CUENTA MATRIZ",
            "CUENTA",
            "ALIADO",
            "CIUDAD",
            "FECHA AGENDA",
            "NOTA",
        ],
        "gpon_bases": [
            "CODIGO",
            "CUENTA",
            "TIPIFICACION REGIONAL",
            "CUENTA MATRIZ",
            "ALIADO",
            "Ciudad",
            "FECHA DE MIGRACION",
        ],
    },
}


# Filtros para cada tipo de análisis
FILTERS = {
    COMERCIAL_EFFICACY_ANALYSIS: {
        "ofsc_dispatch": {
            "include": {
                "Estado": "No completado",
                "Tipo de Actividad": ["Instalaciones", "INSTALACIONES FTTH"],
                "Tipo de Red": ["Pymes", "FTTX"],
            },
        },
        "ofsc_capacity": {
            "include": {
                "Estado": "No completado",
                "Tipo de Actividad": ["Instalaciones", "INSTALACIONES FTTH"],
                "Tipo de Red": ["Pymes", "FTTX"],
            }
        },
    },
    CONTACT_ANALYSIS: {
        "ofsc_capacity": {
            "include": {
                "Tipo de Actividad": ["Instalaciones", "INSTALACIONES FTTH"],
                "Tipo de Red": ["Pymes", "FTTX"],
            }
        },
    },
    BACKLOG_ANALYSIS: {
        "backlog": {
            "include": {
                "Region": "REGION ORIENTE",
            },
            "exclude": {
                "TIPO_TRABAJO": [
                    "Cambio Control",
                    "Demostracion",
                    "Desconexiones",
                    "Reconexiones",
                    "Supervision",
                ],
                "SEGMENTO": [
                    "RE",
                    "RAN",
                    "RAT",
                    "RVA",
                    "REC",
                ],
            },
        },
    },
}


# Nombre de columnas finales para cada análisis
FINAL_COLUMNS = {
    COMERCIAL_EFFICACY_ANALYSIS: {
        "Orden de trabajo": "Orden de Trabajo",
        "Notas de Cierre": "Nota de Cierre",
        "Compañia": "Aliado",
        "Inicio": "Hora",
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
    BACKLOG_ANALYSIS: {
        "TIPO_TRABAJO": "Tipo de Trabajo",
        "TIPO_BACKLOG": "Tipo de Backlog",
        "CUENTA": "Cuenta",
        "OT/LL": "OT",
        "FECHA_CREADO": "Fecha de Creación",
        "CONVENIENCIA": "Convivencia",
        "Comunidad": "Ciudad",
        "FECHA_AGENDA_FUTURO": "Fecha Agenda Futuro",
        "ESTADO_VISITA": "Estado de la Visita",
        "ANTIGUEDAD_ULTIMA_VISITA": "Antiguedad",
        "CUENTA_MATRIZ": "Cuenta Matriz",
        "GV-Especialista": "Especialista",
        "GV-Descripcion": "Proveedor",
        "CANAL2": "Canal",
        "JEFE 1 CANAL REGIONAL": "Jefe de Canal",
    },
    MIGRATIONS_ANALYSIS: {
        "brownfield_bases": {
            "ESTADO REGIONAL": "Estado",
            "CUENTA MATRIZ": "Cuenta Matriz",
            "CUENTA": "Cuenta",
            "ALIADO": "Aliado",
            "CIUDAD": "Ciudad",
            "FECHA AGENDA": "Fecha",
            "TIPIFICACION": "Tipificación",
            "DESMONTE DE NODOS 1": "Desmonte de Nodos",
            "NOTA": "Nota",
        },
        "gpon_bases": {
            "TIPIFICACION REGIONAL": "Estado",
            "CUENTA MATRIZ": "Cuenta Matriz",
            "CUENTA": "Cuenta",
            "ALIADO": "Aliado",
            "Ciudad": "Ciudad",
            "FECHA DE MIGRACION": "Fecha",
            "CODIGO": "Código",
        },
    },
}


# Orden de columnas para el archivo final de cada análisis
COLUMN_ORDER = {
    COMERCIAL_EFFICACY_ANALYSIS: [
        "Orden de Trabajo",
        "Tipo de Actividad",
        "Estado",
        "Razón",
        "Nota de Cierre",
        "Tipo de Red",
        "Aliado",
        "Ciudad",
        "Código del Asesor Comercial",
        "Asesor Comercial",
        "Especialista",
        "Proveedor",
        "Canal",
        "Jefe de Canal",
        "Razón Sugerida",
        "Estado de la Razón",
        "Fecha",
        "Hora",
    ],
    MIGRATIONS_ANALYSIS: [
        "Estado",
        "Cuenta Matriz",
        "Tipo de Red",
        "Cuenta",
        "Aliado",
        "Ciudad",
        "Tipificación",
        "Desmonte de Nodos",
        "Nota",
        "Código",
        "Fecha",
    ],
}


# Archivo de salida
EFFICACY_ANALYSIS_FILE_PATH = PROJECT_ROOT / "datos-efectividad-comercial.xlsx"
PRODUCTIVITY_ANALYSIS_FILE_PATH = PROJECT_ROOT / "datos-productividad.xlsx"
MIGRATIONS_ANALYSIS_FILE_PATH = PROJECT_ROOT / "datos-migraciones.xlsx"
CONTACT_ANALYSIS_FILE_PATH = PROJECT_ROOT / "datos-contacto.xlsx"
BACKLOG_ANALYSIS_FILE_PATH = PROJECT_ROOT / "datos-backlog.xlsx"


# Salidas individuales de archivos de apoyo
COMERCIAL_OFSC_PATH = COMERCIAL_UTILS_FOLDER / "ofsc_capacity_dispatch.xlsx"
COMERCIAL_OFSC_CAPACITY_PATH = COMERCIAL_UTILS_FOLDER / "ofsc_capacity.xlsx"
COMERCIAL_OFSC_DISPATCH_PATH = COMERCIAL_UTILS_FOLDER / "ofsc_dispatch.xlsx"
COMERCIAL_RESIDENTIAL_PLANT_PATH = COMERCIAL_UTILS_FOLDER / "planta_residencial.xlsx"
CONTACT_RESIDENTIAL_PLANT_PATH = CONTACT_UTILS_FOLDER / "planta_residencial.xlsx"
CONTACT_OFSC_CAPACITY_PATH = CONTACT_UTILS_FOLDER / "ofsc_capacity.xlsx"
PRODUCTIVITY_OFSC_FTTH_HFC_PATH = PRODUCTIVITY_UTILS_FOLDER / "ofsc_ftth_hfc.xlsx"
PRODUCTIVITY_OFSC_FO_PATH = PRODUCTIVITY_UTILS_FOLDER / "ofsc_fo.xlsx"
BACKLOG_OFSC_FO_PATH = BACKLOG_UTILS_FOLDER / "backlog.xlsx"
BACKLOG_RESIDENTIAL_PLANT = BACKLOG_UTILS_FOLDER / "planta_residencial.xlsx"

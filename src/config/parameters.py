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
DEBUGGING_FOLDER = PROJECT_ROOT / "debugging"
COMERCIAL_DEBUGGING_FOLDER = DEBUGGING_FOLDER / "comercial"
CONTACT_DEBUGGING_FOLDER = DEBUGGING_FOLDER / "contacto"
BACKLOG_DEBUGGING_FOLDER = DEBUGGING_FOLDER / "backlog"
PRODUCTIVITY_DEBUGGING_FOLDER = DEBUGGING_FOLDER / "productividad"
MIGRATIONS_DEBUGGING_FOLDER = DEBUGGING_FOLDER / "migraciones"
FO_TREE_FOLDER = DATABASES_FOLDER / "FO"
LOGS_FOLDER = PROJECT_ROOT / "logs"


# Configuración de rutas de archivos
RESIDENTIAL_PLANT_PATH = DATABASES_FOLDER / "RM Planta Residencial.xlsb"
BACKLOG_PATH = DATABASES_FOLDER / "Backlog_Nacional_Por_Produccion.csv"
GPON_BASES_PATH = DATABASES_FOLDER / "BASES CENTROS COMERCIALES GPON.xlsx"
BROWNFIELD_BASES_PATH = DATABASES_FOLDER / "BASE BROWNFIELD 2026 Oriente.xlsx"
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
            "Region",
            "CONVENIENCIA",
            "Comunidad",
            "Opera",
            "Red",
            "FECHA_AGENDA_FUTURO",
            "ESTADO_ORDEN",
            "ESTADO_VISITA",
            "ANTIGUEDAD_ULTIMA_VISITA",
            "CUENTA_MATRIZ",
            "CEDULA_VENDEDOR",
            "ANTIGUEDAD_DIGITACION",
            "HORA_CREADO",
            "CLASE",
            "SEGMENTO",
            "Aliado Zonificado",
        ],
        "residential_plant": [
            "TCARGU",
            "CC_COMPLETA",
            "GV-Especialista",
            "GV-Descripcion",
            "JEFE 1 CANAL REGIONAL",
            "CANAL2",
        ],
    },
    MIGRATIONS_ANALYSIS: {
        "brownfield_bases": [
            "ESTADO REGIONAL",
            "CRONOGRAMA DESMONTE REGIONAL",
            "CRONOGRAMA DESMONTE TRANSVERSAL",
            "TIPIFICACION",
            "CUENTA MATRIZ",
            "CRUCE POTENCIAL",
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
            "BASE TV",
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
        "HORA_CREADO": "Hora de Creación",
        "CONVENIENCIA": "Convivencia",
        "ESTADO_ORDEN": "Estado de la Orden",
        "Aliado Zonificado": "Aliado",
        "ANTIGUEDAD_DIGITACION": "Antiguedad desde la Digitación",
        "CLASE": "Clase",
        "CEDULA_VENDEDOR": "Cédula del Vendedor",
        "SEGMENTO": "Segmento",
        "Comunidad": "Ciudad",
        "FECHA_AGENDA_FUTURO": "Fecha Agenda Futuro",
        "ESTADO_VISITA": "Estado de la Visita",
        "ANTIGUEDAD_ULTIMA_VISITA": "Antiguedad desde la Última Visita",
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
            "CRUCE POTENCIAL": "Cruce Potencial",
            "ALIADO": "Aliado",
            "CIUDAD": "Ciudad",
            "FECHA AGENDA": "Fecha",
            "TIPIFICACION": "Tipificación",
            "CRONOGRAMA DESMONTE REGIONAL": "Cronograma Desmonte Regional",
            "CRONOGRAMA DESMONTE TRANSVERSAL": "Cronograma Desmonte Transversal",
            "NOTA": "Nota",
        },
        "gpon_bases": {
            "TIPIFICACION REGIONAL": "Estado",
            "CUENTA MATRIZ": "Cuenta Matriz",
            "CUENTA": "Cuenta",
            "ALIADO": "Aliado",
            "BASE TV": "Cruce Potencial",
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
        "Cruce Potencial",
        "Cronograma Desmonte Regional",
        "Cronograma Desmonte Transversal",
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
COMERCIAL_OFSC_PATH = COMERCIAL_DEBUGGING_FOLDER / "ofsc_capacity_dispatch.xlsx"
COMERCIAL_OFSC_CAPACITY_PATH = COMERCIAL_DEBUGGING_FOLDER / "ofsc_capacity.xlsx"
COMERCIAL_OFSC_DISPATCH_PATH = COMERCIAL_DEBUGGING_FOLDER / "ofsc_dispatch.xlsx"
CONTACT_RESIDENTIAL_PLANT_PATH = CONTACT_DEBUGGING_FOLDER / "planta_residencial.xlsx"
CONTACT_OFSC_CAPACITY_PATH = CONTACT_DEBUGGING_FOLDER / "ofsc_capacity.xlsx"
PRODUCTIVITY_OFSC_FTTH_HFC_PATH = PRODUCTIVITY_DEBUGGING_FOLDER / "ofsc_ftth_hfc.xlsx"
PRODUCTIVITY_OFSC_FO_PATH = PRODUCTIVITY_DEBUGGING_FOLDER / "ofsc_fo.xlsx"
BACKLOG_OFSC_FO_PATH = BACKLOG_DEBUGGING_FOLDER / "backlog.xlsx"
BACKLOG_RESIDENTIAL_PLANT = BACKLOG_DEBUGGING_FOLDER / "planta_residencial.xlsx"
COMERCIAL_RESIDENTIAL_PLANT_PATH = (
    COMERCIAL_DEBUGGING_FOLDER / "planta_residencial.xlsx"
)

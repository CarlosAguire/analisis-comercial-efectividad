from pathlib import Path

from config.env import get_bool_env, load_env

# Configuración de ruta raíz del proyecto
THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parent.parent.parent


# Cargar variables de entorno desde el archivo .env
load_env(env_path=PROJECT_ROOT / ".env")
DEBUG = get_bool_env(key="DEBUG", default=False)


# Configuraciónes y rutas de archivos
DATABASES_FOLDER = PROJECT_ROOT / "databases"
MISSING_FOLDER = PROJECT_ROOT / "missing_files"
FTTH_HFC_FOLDER = MISSING_FOLDER / "FTTH-HFC"
FTTH_HFC_CAPACITY_FOLDER = FTTH_HFC_FOLDER / "Capacidades"
FTTH_HFC_DISPATCH_FOLDER = FTTH_HFC_FOLDER / "Despacho"
FO_FOLDER = MISSING_FOLDER / "FO"
BACKLOG_FOLDER = MISSING_FOLDER / "Backlog"
LOGS_FOLDER = PROJECT_ROOT / "logs"
SRC_FOLDER = PROJECT_ROOT / "src"


# Configuración de formatos de fecha para cada tipo de análisis
FTTH_HFC_CAPACITY_DATE_FORMAT = "dmy"
FTTH_HFC_DISPATCH_DATE_FORMAT = "mdy"
FO_DATE_FORMAT = "dmy"


# Configuración de rutas de archivos
RESIDENTIAL_PLANT_PATH = DATABASES_FOLDER / "RM Planta Residencial.csv"
GPON_BASES_PATH = DATABASES_FOLDER / "BASES CENTROS COMERCIALES GPON.xlsx"
BROWNFIELD_BASES_PATH = DATABASES_FOLDER / "BASE BROWNFIELD 2026 Oriente.xlsx"
RECENT_EXECUTIONS_PATH = SRC_FOLDER / "recent_executions.json"
PY_OUT_LOGS_PATH = LOGS_FOLDER / "py_out_logs.txt"
LOGS_PATH = LOGS_FOLDER / "logs.txt"


# Tipos de análisis
REASONED_ANALYSIS = "análisis de razonadas"
CONTACT_ANALYSIS = "análisis de contacto"
BACKLOG_ANALYSIS = "análisis de backlog"
PRODUCTIVITY_ANALYSIS = "análisis de productividad"
MIGRATIONS_ANALYSIS = "análisis de migraciones"


# Tipos de datos para cada archivo
RESIDENTIAL_PLANT_TYPES = {
    "TCARGU": "string",
    "CC_COMPLETA": "string",
    "NOMBRE": "string",
    "GV-Especialista": "string",
    "GV-Descripcion": "string",
    "CANAL2": "string",
    "JEFE 1 CANAL REGIONAL": "string",
}
FTTH_HFC_CAPACITY_TYPES = {
    "Coordenada X": "string",
    "Coordenada Y": "string",
    "Estado": "string",
    "External ID": "string",
    "Actividad ID": "string",
    "Número de cuenta": "string",
    "Técnico": "string",
    "Tipo de Actividad": "string",
    "Subtipo de la Orden de Trabajo": "string",
    "Ciudad": "string",
    "Duración": "string",
    "Razón": "string",
    "Compañia": "string",
    "Orden de trabajo": "string",
    "Tipo de Red": "string",
    "Asesor comercial": "string",
    "Código Asesor comercial": "string",
    "Ventana de servicio": "string",
    "Intervalos de tiempo": "string",
    "Código de causa 3 del IIMS": "string",
    "Nodo": "string",
    "Fecha": "string",
    "Inicio": "string",
    "Teléfono": "string",
    "Telefono dos del cliente": "string",
    "Teléfono 3": "string",
    "Celuar del contacto": "string",
}
FTTH_HFC_DISPATCH_TYPES = {
    "Notas de Cierre": "string",
    "Notas de Cierre.1": "string",
    "Orden de trabajo": "string",
    "Tipo de Actividad": "string",
    "Tipo de Red": "string",
    "Estado": "string",
    "Fecha": "string",
    "Inicio": "string",
    "Compañia": "string",
}
FO_TYPES = {
    "Coordenada X": "string",
    "Coordenada Y": "string",
    "Estado": "string",
    "External ID": "string",
    "Actividad ID": "string",
    "Número de cuenta": "string",
    "Técnico": "string",
    "Tipo de Actividad": "string",
    "Subtipo de la Orden de Trabajo": "string",
    "Ciudad": "string",
    "Duración": "string",
    "Razón": "string",
    "Compañia": "string",
    "Orden de trabajo": "string",
    "Tipo de Red": "string",
    "Asesor comercial": "string",
    "Código Asesor comercial": "string",
    "Ventana de servicio": "string",
    "Intervalos de tiempo": "string",
    "Código de causa 3 del IIMS": "string",
    "Nodo": "string",
    "Fecha": "string",
    "Inicio": "string",
    "Teléfono": "string",
    "Telefono dos del cliente": "string",
    "Teléfono 3": "string",
    "Celuar del contacto": "string",
}
BACKLOG_TYPES = {
    "TIPO_TRABAJO": "string",
    "TIPO_BACKLOG": "string",
    "CUENTA": "string",
    "OT/LL": "string",
    "Region": "string",
    "CONVENIENCIA": "string",
    "Comunidad": "string",
    "Opera": "string",
    "Red": "string",
    "NODO": "string",
    "REGIONAL": "string",
    "ESTADO_ORDEN": "string",
    "FECHA_AGENDA_FUTURO": "string",
    "ANTIGUEDAD_ULTIMA_VISITA": "string",
    "CUENTA_MATRIZ": "string",
    "CEDULA_VENDEDOR": "string",
    "ANTIGUEDAD_DIGITACION": "string",
    "CLASE": "string",
    "SEGMENTO": "string",
    "Aliado Zonificado": "string",
}
GPON_TYPES = {
    "CODIGO": "string",
    "CUENTA": "string",
    "TIPIFICACION REGIONAL": "string",
    "CUENTA MATRIZ": "string",
    "BASE TV": "string",
    "ALIADO": "string",
    "Ciudad": "string",
    "FECHA DE MIGRACION": "string",
}
BROWNFIELD_TYPES = {
    "ESTADO REGIONAL": "string",
    "CRONOGRAMA DESMONTE REGIONAL": "string",
    "CRONOGRAMA DESMONTE TRANSVERSAL": "string",
    "TIPIFICACION": "string",
    "CUENTA MATRIZ": "string",
    "CRUCE POTENCIAL": "string",
    "CUENTA": "string",
    "ALIADO": "string",
    "CIUDAD": "string",
    "FECHA AGENDA": "string",
    "NOTA": "string",
}


# Lista de columnas a conservarpara cada análisis
COLUMNS_TO_RESERVE = {
    REASONED_ANALYSIS: {
        "dispatch_file": [
            "Notas de Cierre",
            "Notas de Cierre.1",
            "Orden de trabajo",
            "Fecha",
            "Inicio",
            "Compañia",
        ],
        "capacity_file": [
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
        "residential_plant_file": [
            "NOMBRE",
            "GV-Especialista",
            "GV-Descripcion",
            "JEFE 1 CANAL REGIONAL",
            "CANAL2",
        ],
    },
    CONTACT_ANALYSIS: {
        "capacity_file": [
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
        "residential_plant_file": [
            "NOMBRE",
            "GV-Especialista",
            "GV-Descripcion",
            "JEFE 1 CANAL REGIONAL",
            "CANAL2",
        ],
    },
    PRODUCTIVITY_ANALYSIS: {
        "capacity_file": [
            "Técnico",
            "Fecha",
            "Tipo de Actividad",
            "Subtipo de la Orden de Trabajo",
            "Estado",
            "Duración",
            "Ciudad",
            "Número de cuenta",
            "Orden de trabajo",
            "Actividad ID",
            "Intervalos de tiempo",
            "Código de causa 3 del IIMS",
            "Nodo",
            "Tipo de Red",
            "Coordenada X",
            "Coordenada Y",
            "External ID",
            "Compañia",
        ],
        "fo_file": [
            "Técnico",
            "Fecha",
            "Tipo de Actividad",
            "Subtipo de la Orden de Trabajo",
            "Estado",
            "Duración",
            "Ciudad",
            "Número de cuenta",
            "Orden de trabajo",
            "Actividad ID",
            "Intervalos de tiempo",
            "Código de causa 3 del IIMS",
            "Nodo",
            "Tipo de Red",
            "Coordenada X",
            "Coordenada Y",
            "External ID",
            "Compañia",
        ],
    },
    BACKLOG_ANALYSIS: {
        "backlog_file": [
            "TIPO_TRABAJO",
            "TIPO_BACKLOG",
            "CUENTA",
            "OT/LL",
            "Region",
            "CONVENIENCIA",
            "Comunidad",
            "Opera",
            "Red",
            "NODO",
            "ESTADO_ORDEN",
            "FECHA_AGENDA_FUTURO",
            "ANTIGUEDAD_ULTIMA_VISITA",
            "CUENTA_MATRIZ",
            "CEDULA_VENDEDOR",
            "ANTIGUEDAD_DIGITACION",
            "CLASE",
            "SEGMENTO",
            "Aliado Zonificado",
        ],
        "capacity_file": [
            "Orden de trabajo",
            "Estado",
            "Ventana de servicio",
        ],
        "fo_file": [
            "Orden de trabajo",
            "Estado",
            "Ventana de servicio",
        ],
        "residential_plant": [
            "GV-Especialista",
            "GV-Descripcion",
            "JEFE 1 CANAL REGIONAL",
            "CANAL2",
            "CC_COMPLETA",
            "TCARGU",
        ],
    },
}


# Filtros para cada tipo de análisis
FILTERS = {
    REASONED_ANALYSIS: {
        "dispatch_file": {
            "include": {
                "Estado": "No completado",
                "Tipo de Actividad": ["Instalaciones", "INSTALACIONES FTTH"],
                "Tipo de Red": ["Pymes", "FTTX"],
            },
        },
        "capacity_file": {
            "include": {
                "Estado": "No completado",
                "Tipo de Actividad": ["Instalaciones", "INSTALACIONES FTTH"],
                "Tipo de Red": ["Pymes", "FTTX"],
            }
        },
    },
    CONTACT_ANALYSIS: {
        "capacity_file": {
            "include": {
                "Tipo de Actividad": ["Instalaciones", "INSTALACIONES FTTH"],
                "Tipo de Red": ["Pymes", "FTTX"],
            }
        },
    },
    PRODUCTIVITY_ANALYSIS: {
        "capacity_file": {
            "exclude": {
                "Tipo de Actividad": [
                    "Actividades de Almacen",
                    "Almuerzo",
                    "Ausentismo",
                    "Capacitacion",
                    "Otros",
                    "Recursos Humanos",
                    "Permiso",
                ],
            },
        },
        "fo_file": {
            "exclude": {
                "Tipo de Actividad": [
                    "Actividades de Almacen",
                    "Almuerzo",
                    "Ausentismo",
                    "Capacitacion",
                    "Otros",
                    "Recursos Humanos",
                    "Permiso",
                ],
            },
        },
    },
    BACKLOG_ANALYSIS: {
        "backlog_file": {
            "include": {
                "combine": "or",
                "fields": {
                    "Region": "REGION ORIENTE",
                    "REGIONAL": "ROR",
                },
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
        "capacity_file": {
            "exclude": {
                "Tipo de Actividad": [
                    "Actividades de Almacen",
                    "Almuerzo",
                ],
            },
            "include": {
                "Tipo de Red": ["Pymes", "FTTX"],
            },
        },
        "fo_file": {
            "exclude": {
                "Tipo de Actividad": [
                    "Actividades de Almacen",
                    "Almuerzo",
                ],
            },
        },
    },
}


# Nombre de columnas finales para cada análisis
FINAL_COLUMNS = {
    REASONED_ANALYSIS: {
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
        "CONVENIENCIA": "Convivencia",
        "ESTADO_ORDEN": "Estado de la Orden",
        "Aliado Zonificado": "Aliado",
        "ANTIGUEDAD_DIGITACION": "Antiguedad desde la Digitación",
        "CLASE": "Clase",
        "NODO": "Nodo",
        "CEDULA_VENDEDOR": "Cédula del Vendedor",
        "SEGMENTO": "Segmento",
        "Comunidad": "Ciudad",
        "FECHA_AGENDA_FUTURO": "Fecha Agenda Futuro",
        "ANTIGUEDAD_ULTIMA_VISITA": "Antiguedad desde la Última Visita",
        "CUENTA_MATRIZ": "Cuenta Matriz",
        "GV-Especialista": "Especialista",
        "GV-Descripcion": "Proveedor",
        "CANAL2": "Canal",
        "JEFE 1 CANAL REGIONAL": "Jefe de Canal",
    },
    MIGRATIONS_ANALYSIS: {
        "brownfield_file": {
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
        "gpon_file": {
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
    REASONED_ANALYSIS: [
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
    PRODUCTIVITY_ANALYSIS: [
        "Técnico",
        "Intervalos de tiempo",
        "Actividad ID",
        "Fecha",
        "Tipo de Actividad",
        "Subtipo de la Orden de Trabajo",
        "Orden de trabajo",
        "Estado",
        "Duración",
        "Ciudad",
        "Nodo",
        "Número de cuenta",
        "Tipo de Red",
        "Código de causa 3 del IIMS",
        "Compañia",
        "External ID",
        "Coordenada X",
        "Coordenada Y",
    ],
}


# Archivo de salida
REASONED_ANALYSIS_FILE_PATH = PROJECT_ROOT / "datos-razonadas-tmp.xlsx"
PRODUCTIVITY_ANALYSIS_FILE_PATH = PROJECT_ROOT / "datos-productividad-tmp.xlsx"
CONTACT_ANALYSIS_FILE_PATH = PROJECT_ROOT / "datos-contacto-tmp.xlsx"
MIGRATIONS_ANALYSIS_FILE_PATH = PROJECT_ROOT / "datos-migraciones.xlsx"
BACKLOG_ANALYSIS_FILE_PATH = PROJECT_ROOT / "datos-backlog.xlsx"

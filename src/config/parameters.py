from pathlib import Path

# Configuración del modo de ejecución
DEBUG = False


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
BACKLOG_FOLDER = DATABASES_FOLDER / "Back Transversal"


# Tipos de análisis
COMERCIAL_EFFICACY_ANALYSIS = "análisis de efectividad comercial"
CONTACT_ANALYSIS = "análisis de contacto"
BACKLOG_ANALYSIS = "análisis de backlog"
PRODUCTIVITY_ANALYSIS = "análisis de productividad"


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
    PRODUCTIVITY_ANALYSIS: {
        "ofsc_capacity": [
            "Técnico",
            "Intervalos de tiempo",
            "Actividad ID",
            "ID Aliado",
            "Fecha",
            "Nombre",
            "Dirección campo 1",
            "Nombre Completo",
            "Tipo de Actividad",
            "Subtipo de la Orden de Trabajo",
            "Orden de trabajo",
            "Estado",
            "Zonas de trabajo",
            "Duración",
            "Ciudad",
            "Departamento",
            "Nodo",
            "Número de cuenta",
            "Estado interno de la OT",
            "Numero de Reincidencias Serivicios",
            "Numero de Reincidencias Calidad",
            "Numero de Reprogramaciones",
            "SLA Suscriptor",
            "SLA Cumplimiento",
            "Estado SLA",
            "Asesor comercial",
            "Código Asesor comercial",
            "Tipo de Red",
            "Materials Validation Result",
            "Resultados SoftClose",
            "Agent Confirmation",
            "Regional",
            "Unidad de Gestión",
            "Razón",
            "Número de Ticket Fallas Masivas",
            "Código de causa 1 del IIMS",
            "Código de causa 2 del IIMS",
            "Código de causa 3 del IIMS",
            "Fecha de agendamiento",
            "Compañia",
            "External ID",
            "Persona que Confirma",
            "Nombre Completo",
            "Lista de Razon",
            "Prioridad",
            "Teléfono",
            "Telefono dos del cliente",
            "Teléfono 3",
            "Celuar del contacto",
            "Coordenada X",
            "Coordenada Y",
            "Agenda Inmediata",
            "Fecha de creación de la OT YYYY-MM-DD",
        ],
    },
}


# Filtros para cada tipo de análisis
FILTERS = {
    COMERCIAL_EFFICACY_ANALYSIS: {
        "ofsc_dispatch": {
            "include": {
                "Estado": "No completado",
                "Tipo de Actividad": "Instalaciones",
                "Tipo de Red": "Pymes",
            },
        },
        "ofsc_capacity": {
            "include": {
                "Estado": "No completado",
                "Tipo de Actividad": "Instalaciones",
                "Tipo de Red": "Pymes",
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
}


# Archivo de salida
EFFICACY_ANALYSIS_FILE_PATH = PROJECT_ROOT / "datos-efectividad-comercial.xlsx"
CONTACT_ANALYSIS_FILE_PATH = PROJECT_ROOT / "datos-analisis-contacto.xlsx"
BACKLOG_ANALYSIS_FILE_PATH = PROJECT_ROOT / "backlog.xlsx"
PRODUCTIVITY_ANALYSIS_FILE_PATH = PROJECT_ROOT / "AVANCE DIARIO.xlsx"


# Salidas individuales de archivos de apoyo
UTILS_FOLDER.mkdir(parents=True, exist_ok=True)
CLEAN_OFSC_PATH = UTILS_FOLDER / "limpio_ofsc.xlsx"
CLEAN_OFSC_CAPACITY_PATH = UTILS_FOLDER / "limpio_ofsc_capacity.xlsx"
CLEAN_OFSC_DISPATCH_PATH = UTILS_FOLDER / "limpio_ofsc_dispatch.xlsx"
CLEAN_RESIDENTIAL_PLANT_PATH = UTILS_FOLDER / "limpio_planta_residencial.xlsx"
LOGS_PATH = LOGS_FOLDER / "logs.txt"
PY_OUT_LOGS_PATH = LOGS_FOLDER / "py_out_logs.txt"
